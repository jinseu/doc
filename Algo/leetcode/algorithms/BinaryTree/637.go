func averageOfLevel(nodeSlice []*TreeNode) (nextNodeSlice []*TreeNode, avg float64) {
    var sum float64

    num := len(nodeSlice)
    for _, node := range nodeSlice {
        sum += float64(node.Val)
        if nil != node.Left {
            nextNodeSlice = append(nextNodeSlice, node.Left)
        }
        if nil != node.Right {
            nextNodeSlice = append(nextNodeSlice, node.Right)
        }
    }

    avg = sum / float64(num)

    return nextNodeSlice, avg
}

func averageOfLevels(root *TreeNode) []float64 {
    var ret []float64
    var avg float64
    nextNodeSlice := []*TreeNode{root}

    for ; len(nextNodeSlice) > 0; {
        nextNodeSlice, avg = averageOfLevel(nextNodeSlice)
        ret = append(ret, avg)
    }

    return ret
}
