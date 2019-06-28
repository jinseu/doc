### etcd

etcd的官方介绍是Etcd is a distributed, consistent key-value store for shared configuration and service discovery。

#### 基本使用

1. 提供存储以及获取数据的接口，它通过协议保证 Etcd 集群中的多个节点数据的强一致性。用于存储元信息以及共享配置。
2. 提供监听机制，客户端可以监听某个key或者某些key的变更，用于监听和推送变更。
3. 提供key的过期以及续约机制，客户端通过定时刷新来实现续约。用于集群监控以及服务注册发现。
4. 提供原子的CAS（Compare-and-Swap）支持。用于分布式锁以及leader选举。

etcd 的LogEntry 由四个部分组成：

1. type，只有两种，一种是0表示Normal，1表示ConfChange（ConfChange表示 Etcd 本身的配置变更同步，比如有新的节点加入等）。
2. term，每个term代表一个主节点的任期，每次主节点变更term就会变化。
3. index，这个序号是严格有序递增的，代表变更序号。
4. 二进制的data，将raft request对象的pb结构整个保存下。

**etcd v3与v2的不同**

1. 接口通过grpc提供rpc接口，放弃了v2的http接口。优势是长连接效率提升明显，缺点是使用不如以前方便，尤其对不方便维护长连接的场景。
2. 废弃了原来的目录结构，变成了纯粹的kv，用户可以通过前缀匹配模式模拟目录。
3. 内存中不再保存value，同样的内存可以支持存储更多的key。
4. watch机制更稳定，基本上可以通过watch机制实现数据的完全同步。
5. 提供了批量操作以及事务机制，用户可以通过批量事务请求来实现Etcd v2的CAS机制（批量事务支持if条件判断）。

#### 基本API

**Key-Value API**

基本key-value 结构如下

```
message KeyValue {
  bytes key = 1;
  int64 create_revision = 2;
  int64 mod_revision = 3;
  int64 version = 4;
  bytes value = 5;
  int64 lease = 6;
}
```

其中字段含义如下:

1. 每一个etcd集群，都有两个全局变量`revision`和`raft_term`。
 - `revision`是一个64-bit全局单调递增变量，每次`key`更改的时候，都会递增，相当于全局的逻辑时钟。新的`revision`意味着在全局B+树中已经写入了更新。
 - `raft_term`，代表主节点的任期，每次主节点变更term就会递增。
2. 每一个`key/value` 都有一个version表示这个key的版本，`create_revision`记录了创建时的revision，`mod_revision`则记录了最后一次变更（包括PUT，Txn)时的`revision`。
3. lease 表示相关联的lease的id，当关联的lease过期时，key也会被删除

在etcd 中不再是简单的get一个变量，而是以range的形式获取一定范围的内的所有key。RangeRequest的结构如下，可以看到通过range形式，提供了强大的功能。同样的，在删除时，也是以Range的形式删除。

```
message RangeRequest {
  enum SortOrder {
	NONE = 0;    // default, no sorting
	ASCEND = 1;  // lowest target value first
	DESCEND = 2; // highest target value first
  }
  enum SortTarget {
	KEY = 0;
	VERSION = 1;
	CREATE = 2;
	MOD = 3;
	VALUE = 4;
  }

  bytes key = 1;
  bytes range_end = 2;
  int64 limit = 3;
  int64 revision = 4;
  SortOrder sort_order = 5;
  SortTarget sort_target = 6;
  bool serializable = 7;
  bool keys_only = 8;
  bool count_only = 9;
  int64 min_mod_revision = 10;
  int64 max_mod_revision = 11;
  int64 min_create_revision = 12;
  int64 max_create_revision = 13;
}
```

**Transaction**

transaction 是一个原子的If/Then/Else操作，类似于CAS。可以原子的处理多个请求，即一个tansaction即使有多个操作，revision也只增加一次。**在一个tansaction不能更新同一个键多次，tansaction只能对一个已有的kv和给定的常量对比，不能对两个kv进行对比。**

```
message TxnRequest {
  repeated Compare compare = 1;
  repeated RequestOp success = 2;
  repeated RequestOp failure = 3;
}
message RequestOp {
  // request is a union of request types accepted by a transaction.
  oneof request {
    RangeRequest request_range = 1;
    PutRequest request_put = 2;
    DeleteRangeRequest request_delete_range = 3;
  }
}
message Compare {
  enum CompareResult {
    EQUAL = 0;
    GREATER = 1;
    LESS = 2;
    NOT_EQUAL = 3;
  }
  enum CompareTarget {
    VERSION = 0;
    CREATE = 1;
    MOD = 2;
    VALUE= 3;
  }
  CompareResult result = 1;
  // target is the key-value field to inspect for the comparison.
  CompareTarget target = 2;
  // key is the subject key for the comparison operation.
  bytes key = 3;
  oneof target_union {
    int64 version = 4;
    int64 create_revision = 5;
    int64 mod_revision = 6;
    bytes value = 7;
  }
}

```

**Watch API**

watch 是一个grpc stream to stream的接口，客户端写入watch request，etcd返回event。watch保证event是原子的，可靠的，有序的。WatchCreateRequest的格式如下:

```
# rpc 定义
rpc Watch(stream WatchRequest) returns (stream WatchResponse)

# WatchCreateRequest 定义
message WatchCreateRequest {
  bytes key = 1;
  bytes range_end = 2;
  int64 start_revision = 3;
  bool progress_notify = 4;

  enum FilterType {
    NOPUT = 0;
    NODELETE = 1;
  }
  repeated FilterType filters = 5;
  bool prev_kv = 6;
}

# WatchCreateRequest 定义
message WatchResponse {
  ResponseHeader header = 1;
  // watch_id is the ID of the watcher that corresponds to the response.
  int64 watch_id = 2;
  // created is set to true if the response is for a create watch request.
  // The client should record the watch_id and expect to receive events for
  // the created watcher from the same stream.
  // All events sent to the created watcher will attach with the same watch_id.
  bool created = 3;
  // canceled is set to true if the response is for a cancel watch request.
  // No further events will be sent to the canceled watcher.
  bool canceled = 4;
  // compact_revision is set to the minimum index if a watcher tries to watch
  // at a compacted index.
  //
  // This happens when creating a watcher at a compacted revision or the watcher cannot
  // catch up with the progress of the key-value store.
  //
  // The client should treat the watcher as canceled and should not try to create any
  // watcher with the same start_revision again.
  int64 compact_revision  = 5;

  // cancel_reason indicates the reason for canceling the watcher.
  string cancel_reason = 6;

  repeated mvccpb.Event events = 11;
}

# event 定义
message Event {
  enum EventType {
    PUT = 0;
    DELETE = 1;
  }
  // type is the kind of event. If type is a PUT, it indicates
  // new data has been stored to the key. If type is a DELETE,
  // it indicates the key was deleted.
  EventType type = 1;
  // kv holds the KeyValue for the event.
  // A PUT event contains current kv pair.
  // A PUT event with kv.Version=1 indicates the creation of a key.
  // A DELETE/EXPIRE event contains the deleted key with
  // its modification revision set to the revision of deletion.
  KeyValue kv = 2;

  // prev_kv holds the key-value pair before the event happens.
  KeyValue prev_kv = 3;
}
```

`start_revision`指定了从某个特定的revision开始，`Progress_Notify`意味着在没有事件发生的情况下周期性收到WatchResponse（with no events）,发送的间隔则由etcd决定。

**Lease API**

lease 在创建时需要提供ttl以及id（如果没有id，etcd会默认分配），然后需要定期Keep alives，删除的时候调用revoke即可。lease 删除的时候关联的key也会被删除。lease相关的api比较简单，在此不再详述。


#### 关键源码解析

**数据存储**

etcd根本上来说是一个k-v存储，它在内存中维护了一个btree（B树），就和mysql的索引一样，它是有序的。具体代码如下:


```
# /mvcc/index.go

type treeIndex struct {
    sync.RWMutex
    tree *btree.BTree
}
```

当存储大量的k-v时，因为用户的value一般比较大，全部放在内存btree里内存耗费过大，所以etcd将用户value保存在磁盘中。

简单的说，etcd是纯内存索引，数据在磁盘持久化。在磁盘上，etcd使用了一个叫做bbolt的纯K-V存储引擎（可以理解为leveldb），那么bbolt的key就需要考虑mvcc了

**MVCC**

为了实现mvcc，etcd中有revision的概念，从接口获取的revision是一个int 64，但内部的revision是一个结构体，由main和sub两部分组成。

```
# /mvcc/revision.go

// A revision indicates modification of the key-value space.
// The set of changes that share same main revision changes the key-value space atomically.
type revision struct {
    // main is the main revision of a set of changes that happen atomically.
    main int64

    // sub is the the sub revision of a change in a set of changes that happen
    // atomically. Each change has different increasing sub revision in that set.
    sub int64
}
```

在内存索引中，每个用户原始key会关联一个`key_index`结构，里面维护了多版本信息，其中modified字段记录了最后一次修改时的revision信息。

generations数组则是真正保存了多版本信息。generations[i]可以看做是第i代，当一个key从无到有的时候，generations[0]会被创建，其created字段记录了引起本次key创建的revision信息。

当用户继续更新这个key的时候，generations[0].revs数组会不断追加记录本次的revision信息。在多版本中，每一次操作行为都被单独记录下来，用户value则是被保存到bbolt中。bbolt中，每个revision将作为key，vlaue则是对应版本的etcd key对应的值。具体的代码可以参见下方的代码段。

其中Tombstone就是指delete删除key，一旦发生删除就会结束当前的generation，生成新的generation，小括号里的(t)标识tombstone。compact(n)表示压缩掉revision.main <= n的所有历史版本，会发生一系列的删减操作，可以仔细观察上述流程。


```
/ keyIndex stores the revisions of a key in the backend.
// Each keyIndex has at least one key generation.
// Each generation might have several key versions.
// Tombstone on a key appends an tombstone version at the end
// of the current generation and creates a new empty generation.
// Each version of a key has an index pointing to the backend.
//
// For example: put(1.0);put(2.0);tombstone(3.0);put(4.0);tombstone(5.0) on key "foo"
// generate a keyIndex:
// key:     "foo"
// rev: 5
// generations:
//    {empty}
//    {4.0, 5.0(t)}
//    {1.0, 2.0, 3.0(t)}
//
// Compact a keyIndex removes the versions with smaller or equal to
// rev except the largest one. If the generation becomes empty
// during compaction, it will be removed. if all the generations get
// removed, the keyIndex should be removed.
//
// For example:
// compact(2) on the previous example
// generations:
//    {empty}
//    {4.0, 5.0(t)}
//    {2.0, 3.0(t)}
//
// compact(4)
// generations:
//    {empty}
//    {4.0, 5.0(t)}
//
// compact(5):
// generations:
//    {empty} -> key SHOULD be removed.
//
// compact(6):
// generations:
//    {empty} -> key SHOULD be removed.
type keyIndex struct {
    key         []byte
    modified    revision // the main rev of the last modification
    generations []generation
}

type generation struct {
    ver     int64
    created revision // when the generation is created (put in first revision).
    revs    []revision
}
```

**watch**

在解释了基本的存储之后，就会发现watch机制的实现便显而易见，watch是基于mvcc多版本实现的。

客户端一个要监听的revision.main作为watch的起始ID，只要etcd当前的全局自增事务ID > watch起始ID，etcd就会将MVCC在bbolt中存储的所有历史revision数据，逐一顺序的推送给客户端。

etcd会保存每个客户端发来的watch请求，watch请求可以关注一个key，或者一个key range（本质上都是range）。

etcd会有一个协程持续不断的遍历所有的watch请求，每个watch对象都维护了其watch的key事件推送到了哪个revision。

etcd会拿着这个revision.main ID去bbolt中继续向后遍历，实际上bbolt类似于leveldb，是一个按key有序的K-V引擎，而bbolt中的key是revision.main+revision.sub组成的，所以遍历就会依次经过历史上发生过的所有事务(tx)记录。

对于遍历经过的每个k-v，etcd会反序列化其中的value，也就是mvccpb.KeyValue，判断其中的Key是否为watch请求关注的key，如果是就发送给客户端。

```
func (s *watchableStore) syncWatchers() int {
    s.mu.Lock()
    defer s.mu.Unlock()

    if s.unsynced.size() == 0 {
        return 0
    }

    s.store.revMu.RLock()
    defer s.store.revMu.RUnlock()

    // in order to find key-value pairs from unsynced watchers, we need to
    // find min revision index, and these revisions can be used to
    // query the backend store of key-value pairs
    curRev := s.store.currentRev
    compactionRev := s.store.compactMainRev

    wg, minRev := s.unsynced.choose(maxWatchersPerSync, curRev, compactionRev)
    minBytes, maxBytes := newRevBytes(), newRevBytes()
    revToBytes(revision{main: minRev}, minBytes)
    revToBytes(revision{main: curRev + 1}, maxBytes)

    // UnsafeRange returns keys and values. And in boltdb, keys are revisions.
    // values are actual key-value pairs in backend.
    tx := s.store.b.ReadTx()
    tx.Lock()
    revs, vs := tx.UnsafeRange(keyBucketName, minBytes, maxBytes, 0)
    evs := kvsToEvents(wg, revs, vs)
    tx.Unlock()
    // event to watch Response 的代码省略
```


它会每次从所有的watcher选出一批watcher进行批处理（组成为一个group，叫做watchGroup），这批watcher中观察的最小revision.main ID作为bbolt的遍历起始位置，这是一种优化。

你可以想一下，如果为每个watcher单独遍历bbolt并从中摘出属于自己关注的key，那性能就太差了。通过一次性遍历，处理多个watcher，显然可以有效减少遍历的次数。

也许你觉得这样在watcher数量多的情况下性能仍旧很差，但是你需要知道一般的用户行为都是从最新的Revision开始watch，很少有需求关注到很古老的revision，这就是关键。

遍历bbolt时，json反序列化每个mvccpb.KeyValue结构，判断其中的key是否属于watchGroup关注的key，这是由kvsToEvents函数完成的。

```
// kvsToEvents gets all events for the watchers from all key-value pairs
func kvsToEvents(wg *watcherGroup, revs, vals [][]byte) (evs []mvccpb.Event) {
    for i, v := range vals {
        var kv mvccpb.KeyValue
        if err := kv.Unmarshal(v); err != nil {
            plog.Panicf("cannot unmarshal event: %v", err)
        }

        if !wg.contains(string(kv.Key)) {
            continue
        }

        ty := mvccpb.PUT
        if isTombstone(revs[i]) {
            ty = mvccpb.DELETE
            // patch in mod revision so watchers won't skip
            kv.ModRevision = bytesToRev(revs[i]).main
        }
        evs = append(evs, mvccpb.Event{Kv: &kv, Type: ty})
    }
    return evs
}
```

最后需要说明的是删除key对应的revision也会保存到bbolt中，只是bbolt的key比较特别，由main+sub+”t”构成，普通的put的key 由main+sub构成。

#### 注释

1. `<-chan int`是一个管道类型，它叫做单向channel。如果是`<-chan int`，说明是只能读不能写的管道（也不能关闭），如果是`chan <- int`，说明是只能写不能读的管道（可以关闭）。

#### 参考链接

> https://draveness.me/etcd-introduction
