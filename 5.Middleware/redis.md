## redis

版本：redis 2.8

**注意：Redis支持多个数据库，并且每个数据库的数据是隔离的不能共享，并且基于单机才有，如果是集群就没有数据库的概念。**

Redis是一个字典结构的存储服务器，而实际上一个Redis实例提供了多个用来存储数据的字典，客户端可以指定将数据存储在哪个字典中。这与我们熟知的在一个关系数据库实例中可以创建多个数据库类似，所以可以将其中的每个字典都理解成一个独立的数据库。

每个数据库对外都是一个从0开始的递增数字命名，Redis默认支持16个数据库（可以通过配置文件支持更多，无上限），可以通过配置databases来修改这一数字。客户端与Redis建立连接后会自动选择0号数据库，不过可以随时使用SELECT命令更换数据库，如要选择1号数据库：

```
redis> SELECT 1
OK
redis [1] > GET foo
(nil)
```

### 基本命令

目前redis功能已经非常强大，支持的功能包括K/V存储，发布/订阅，事务等。其中在K/V存储中，Key的类型是String，值的类型可以是String，List，Set，SortedSet，GEO（地理位置）。

#### KEY

KEY相关的常见操作有以下这些

1. DEL 删除KEY
2. EXISTS 判断是否存在key，存在返回1，不存在返回0
3. DUMP 命令对值进行序列化。
4. EXPIRE、PEXPIRE 命令设置k的TTL，如果已经设置过，则更新。EXPIRE单位为秒，PEXPIRE单位为毫秒。
5. KEYS 命令查找符合pattern的key
6. TTL、PTTL 命令用来查询KEY的TTL，其中TTL以秒为单位，PTTL以毫秒为单位。
7. PERSIST 持久化一个key，并不是保存到硬盘中，而是移除TTL
8. MIGRATE 将 key 原子性地从当前实例传送到目标实例的指定数据库上，一旦传送成功， key 保证会出现在目标实例上，而当前实例上的 key 会被删除。
9. TYPE 返回 key 所储存的值
10. `RESTORE key ttl serialized-value [REPLACE]`，反序列化给定的序列化值，并将它和给定的 key 关联。
11. RANDOMKEY 随机返回一个KEY
12. DBSIZE 获取目前KEY的数量

以下命令原语需要特别说明

**SORT**

基本命令格式为

`SORT key [BY pattern] [LIMIT offset count] [GET pattern [GET pattern ...]] [ASC | DESC] [ALPHA] [STORE destination]`

SORT 对KEY的VALUE进行排序，同时可以将排序后的结果保存到另一个KEY对应的VALUE上。 

**OBJECT**

OBJECT 命令允许从内部察看给定 key 的 Redis 对象。

OBJECT 命令有多个子命令：

* OBJECT REFCOUNT <key> 返回给定 key 引用所储存的值的次数。此命令主要用于除错。
* OBJECT ENCODING <key> 返回给定 key 锁储存的值所使用的内部表示(representation)。
* OBJECT IDLETIME <key> 返回给定 key 自储存以来的空闲时间(idle， 没有被读取也没有被写入)，以秒为单位。
对象可以以多种方式编码：
* 字符串可以被编码为 raw (一般字符串)或 int (为了节约内存，Redis 会将字符串表示的 64 位有符号整数编码为整数来进行储存）。
* 列表可以被编码为 ziplist 或 linkedlist 。 ziplist 是为节约大小较小的列表空间而作的特殊表示。
* 集合可以被编码为 intset 或者 hashtable 。 intset 是只储存数字的小集合的特殊表示。
* 哈希表可以编码为 zipmap 或者 hashtable 。 zipmap 是小哈希表的特殊表示。
* 有序集合可以被编码为 ziplist 或者 skiplist 格式。 ziplist 用于表示小的有序集合，而 skiplist 则用于表示任何大小的有序集合。

**SCAN**

`SCAN cursor [MATCH pattern] [COUNT count]`

SCAN 命令及其相关的 SSCAN 命令、 HSCAN 命令和 ZSCAN 命令都用于增量地迭代（incrementally iterate）一集元素（a collection of elements）：

* SCAN 命令用于迭代当前数据库中的数据库键。
* SSCAN 命令用于迭代集合键中的元素。
* HSCAN 命令用于迭代哈希键中的键值对。
* ZSCAN 命令用于迭代有序集合中的元素（包括元素成员和元素分值）

SCAN 命令的回复是一个包含两个元素的数组， 第一个数组元素是用于进行下一次迭代的新游标， 而第二个数组元素则是一个数组， 这个数组中包含了所有被迭代的元素。如果返回的游标为0，表示已经迭代到结束。SCAN 命令， 以及其他增量式迭代命令， 在进行完整遍历的情况下可以为用户带来以下保证： 从完整遍历开始直到完整遍历结束期间， 一直存在于数据集内的所有元素都会被完整遍历返回。

虽然增量式迭代命令不保证每次迭代所返回的元素数量， 但我们可以使用 COUNT 选项， 对命令的行为进行一定程度上的调整。COUNT 参数的默认值为 10 。

* 在迭代一个足够大的、由哈希表实现的数据库、集合键、哈希键或者有序集合键时， 如果用户没有使用 MATCH 选项， 那么命令返回的元素数量通常和 COUNT 选项指定的一样， 或者比 COUNT 选项指定的数量稍多一些。
* 在迭代一个编码为整数集合（intset，一个只由整数值构成的小集合）、 或者编码为压缩列表（ziplist，由不同值构成的一个小哈希或者一个小有序集合）时， 增量式迭代命令通常会无视 COUNT 选项指定的值， 在第一次迭代就将数据集包含的所有元素都返回给用户。


#### Value

##### String

在value为String类型时，常见的操作如下

* `SET` 设置value
* `APPEND` 在value中增加内容，如果key不存在，则相当于set
* `BITCOUNT key [start] [end] `计算给定字符串中，被设置为 1 的比特位的数量。
* `INCR key` 将 key 中储存的数字值增一
* `DECR key` 将 key 中储存的数字值减一
* `INCRBY key increment` 将 key 所储存的值加上增量 increment 。如果 key 不存在，那么 key 的值会先被初始化为 0 ，然后再执行 INCRBY 命令。
* `DECRBY key decrement` 将 key 所储存的值减去减量 decrement 。
* `STRLEN key` 返回 key 所储存的字符串值的长度。
* `SETEX key seconds value` 将值 value 关联到 key ，并将 key 的生存时间设为 seconds (以秒为单位)。
* `MGET key [key ...]` 返回所有(一个或多个)给定 key 的值。
* `MSET key value [key value ...]` 同时设置一个或多个 key-value 对。


**BITOP**

`BITOP operation destkey key [key ...]`

对一个或多个保存二进制位的字符串 key 进行位元操作，并将结果保存到 destkey 上。

operation 可以是 AND 、 OR 、 NOT 、 XOR 这四种操作中的任意一种：

* BITOP AND destkey key [key ...] ，对一个或多个 key 求逻辑并，并将结果保存到 destkey 。
* BITOP OR destkey key [key ...] ，对一个或多个 key 求逻辑或，并将结果保存到 destkey 。
* BITOP XOR destkey key [key ...] ，对一个或多个 key 求逻辑异或，并将结果保存到 destkey 。
* BITOP NOT destkey key ，对给定 key 求逻辑非，并将结果保存到 destkey 。

**GETBIT/SETBIT**

`SETBIT key offset value`

对 key 所储存的字符串值，设置或清除指定偏移量上的位(bit)。

位的设置或清除取决于 value 参数，可以是 0 也可以是 1 。

当 key 不存在时，自动生成一个新的字符串值。

字符串会进行伸展(grown)以确保它可以将 value 保存在指定的偏移量上。当字符串值进行伸展时，空白位置以 0 填充。

`GETBIT key offset`

对 key 所储存的字符串值，获取指定偏移量上的位(bit)。

当 offset 比字符串值的长度大，或者 key 不存在时，返回 0 。

样例如下

```
127.0.0.1:6379> setbit test 0 1
(integer) 0
127.0.0.1:6379> get test
"\x80"
127.0.0.1:6379> setbit test 15 1
(integer) 0
127.0.0.1:6379> get test
"\x80\x01"
```


**GETRANGE/SETRANGE**

`SETRANGE key offset value` 以字节为单位

用 value 参数覆写(overwrite)给定 key 所储存的字符串值，从偏移量 offset 开始。不存在的 key 当作空白字符串处理。

SETRANGE 命令会确保字符串足够长以便将 value 设置在指定的偏移量上，如果给定 key 原来储存的字符串长度比偏移量小(比如字符串只有 5 个字符长，但你设置的 offset 是 10 )，那么原字符和偏移量之间的空白将用零字节(zerobytes, "\x00" )来填充。

`GETRANGE key start end`

返回 key 中字符串值的子字符串，字符串的截取范围由 start 和 end 两个偏移量决定(包括 start 和 end 在内)。

负数偏移量表示从字符串最后开始计数， -1 表示最后一个字符， -2 表示倒数第二个，以此类推。


#### 事务

redis 的事务比较简单，本质上类似于多行原子执行，并不是完全类似与MySQL的事务。

一个事务以MULTI命令开始，以DISCARD/EXEC 结束。DISCARD表示取消，EXEC表示执行。

WATCH 监视一个(或多个) key ，如果在事务执行之前这个(或这些) key 被其他命令所改动，那么事务将被打断。UNWATCH 则是取消 WATCH 命令对所有 key 的监视。如果在执行 WATCH 命令之后， EXEC 命令或 DISCARD 命令先被执行了的话，那么就不需要再执行 UNWATCH 了。因为 EXEC 命令会执行事务，因此 WATCH 命令的效果已经产生了；而 DISCARD 命令在取消事务的同时也会取消所有对 key 的监视，因此这两个命令执行之后，就没有必要执行 UNWATCH 了。

#### 发布/订阅

redis 提供了发布/订阅功能，用户可以订阅一个channel，或者往一个或者多个channel中发布消息。

* `PUBLISH channel message` 发布消息到一个channel
* `SUBSCRIBE channel [channel ...]` 订阅给定的一个或多个频道的信息。
* `PSUBSCRIBE pattern [pattern ...]` 每个模式以 * 作为匹配符，比如 it* 匹配所有以 it 开头的频道( it.news 、 it.blog 、 it.tweets 等等)， news.* 匹配所有以 news. 开头的频道( news.it 、 news.global.today 等等)，诸如此类。
* `UNSUBSCRIBE [channel [channel ...]]` 指示客户端退订给定的频道

订阅一个或多个符合给定模式的频道。

### 编程使用

### 源码解析

#### SDS

在redis 中键、值都可能是字符串，就算值是列表或者Set，也是由字符串组成的。所以，在redis中最基本的就是字符串的表示。

在redis中，字符串是用sds(Simple Dynamic String）表示的。从redis 3.0开始，sds的定义如下：

```
typedef char *sds;

/* Note: sdshdr5 is never used, we just access the flags byte directly.
 * However is here to document the layout of type 5 SDS strings. */
struct __attribute__ ((__packed__)) sdshdr5 {
    unsigned char flags; /* 3 lsb of type, and 5 msb of string length */
    char buf[];
};
struct __attribute__ ((__packed__)) sdshdr8 {
    uint8_t len; /* used */
    uint8_t alloc; /* excluding the header and null terminator */
    unsigned char flags; /* 3 lsb of type, 5 unused bits */
    char buf[];
};
struct __attribute__ ((__packed__)) sdshdr16 {
    uint16_t len; /* used */
    uint16_t alloc; /* excluding the header and null terminator */
    unsigned char flags; /* 3 lsb of type, 5 unused bits */
    char buf[];
};
struct __attribute__ ((__packed__)) sdshdr32 {
    uint32_t len; /* used */
    uint32_t alloc; /* excluding the header and null terminator */
    unsigned char flags; /* 3 lsb of type, 5 unused bits */
    char buf[];
};
struct __attribute__ ((__packed__)) sdshdr64 {
    uint64_t len; /* used */
    uint64_t alloc; /* excluding the header and null terminator */
    unsigned char flags; /* 3 lsb of type, 5 unused bits */
    char buf[];
};

// 具体定义时有5种sdshdr，但是实际使用时都是以sds的形式出现，sds实际指向buf数组，每个sds前面有sds的头部，就是上面五种sdshdr。获取sds字符串所在位置的两个宏如下。

// 宏定义, 用来获取SDS存储的字符串所在的位置， ## 用来链接两个变量， # 用来将变量转换为字符串
#define SDS_HDR_VAR(T,s) struct sdshdr##T *sh = (void*)((s)-(sizeof(struct sdshdr##T)));
#define SDS_HDR(T,s) ((struct sdshdr##T *)((s)-(sizeof(struct sdshdr##T))))



// 为了性能考虑，sds 所有的函数都被声明为static inline。static inline的内联函数，一般情况下不会产生函数本身的代码，而是全部被嵌入在被调用的地方。如果不加static，则表示该函数有可能会被其他编译单元所调用，所以一定会产生函数本身的代码。所以加了static，一般可令可执行文件变小。内核里一般见不到只用inline的情况，而都是使用static inline。可参见 https://gist.github.com/htfy96/50308afc11678d2e3766a36aa60d5f75
// 计算sds的长度时，首先取出flags，即sds[-1]，然后用SDS_HDR 宏将sds转换为sdshdr，并取出len变量
static inline size_t sdslen(const sds s) {
    unsigned char flags = s[-1];
    switch(flags&SDS_TYPE_MASK) {
        case SDS_TYPE_5:
            return SDS_TYPE_5_LEN(flags);
        case SDS_TYPE_8:
            return SDS_HDR(8,s)->len;
        case SDS_TYPE_16:
            return SDS_HDR(16,s)->len;
        case SDS_TYPE_32:
            return SDS_HDR(32,s)->len;
        case SDS_TYPE_64:
            return SDS_HDR(64,s)->len;
    }
    return 0;
}

// 计算sds可用数值
static inline size_t sdsavail(const sds s) {
    unsigned char flags = s[-1];
    switch(flags&SDS_TYPE_MASK) {
        case SDS_TYPE_5: {
            return 0;
        }
        case SDS_TYPE_8: {
            SDS_HDR_VAR(8,s);
            return sh->alloc - sh->len;
        }
        case SDS_TYPE_16: {
            SDS_HDR_VAR(16,s);
            return sh->alloc - sh->len;
        }
        case SDS_TYPE_32: {
            SDS_HDR_VAR(32,s);
            return sh->alloc - sh->len;
        }
        case SDS_TYPE_64: {
            SDS_HDR_VAR(64,s);
            return sh->alloc - sh->len;
        }
    }
    return 0;
}

```

SDS一共有5种类型的header。目的是节省内存。

一个SDS字符串的完整结构，由在内存地址上前后相邻的两部分组成：

* 一个header。通常包含字符串的长度(len)、最大容量(alloc)和flags。sdshdr5有所不同。

* 一个字符数组。这个字符数组的长度等于最大容量+1。真正有效的字符串数据，其长度通常小于最大容量。在真正的字符串数据之后，是空余未用的字节（一般以字节0填充），允许在不重新分配内存的前提下让字符串数据向后做有限的扩展。在真正的字符串数据之后，还有一个NULL结束符，即ASCII码为0的’\0’字符。这是为了和传统C字符串兼容。之所以字符数组的长度比最大容量多1个字节，就是为了在字符串长度达到最大容量时仍然有1个字节存放NULL结束符。

除了sdshdr5之外，其它4个header的结构都包含3个字段：

* len: 表示字符串的真正长度（不包含NULL结束符在内）。

* alloc: 表示字符串的最大容量（不包含最后多余的那个字节）。

* flags: 总是占用一个字节。其中的最低3个bit用来表示header的类型。

在各个header的类型定义中，还有几个需要我们注意的地方：

* 在各个header的定义中使用了__attribute__ ((packed))，是为了让编译器以紧凑模式来分配内存。如果没有这个属性，编译器可能会为struct的字段做优化对齐，在其中填充空字节。那样的话，就不能保证header和sds的数据部分紧紧前后相邻，也不能按照固定向低地址方向偏移1个字节的方式来获取flags字段了。

* 在各个header的定义中最后有一个char buf[]。我们注意到这是一个没有指明长度的字符数组，这是C语言中定义字符数组的一种特殊写法，称为柔性数组（flexible array member），只能定义在一个结构体的最后一个字段上。它在这里只是起到一个标记的作用，表示在flags字段后面就是一个字符数组，或者说，它指明了紧跟在flags字段后面的这个字符数组在结构体中的偏移位置。而程序在为header分配的内存的时候，它并不占用内存空间。如果计算sizeof(struct sdshdr16)的值，那么结果是5个字节，其中没有buf字段。
* sdshdr5与其它几个header结构不同，它不包含alloc字段，而长度使用flags的高5位来存储。因此，它不能为字符串分配空余空间。如果字符串需要动态增长，那么它就必然要重新分配内存才行。所以说，这种类型的sds字符串更适合存储静态的短字符串（长度小于32）。

以上的定义会带来如下好处：

* header和数据相邻，而不用分成两块内存空间来单独分配。这有利于减少内存碎片，提高存储效率（memory efficiency）。

* 虽然header有多个类型，但sds可以用统一的`char *` 来表达。且它与传统的C语言字符串保持类型兼容。如果一个sds里面存储的是可打印字符串，那么我们可以直接把它传给C函数，比如使用strcmp比较字符串大小，或者使用printf进行打印。



