import math

class Solution(object):
    def poorPigs(self, buckets, minutesToDie, minutesToTest):
        """
        :type buckets: int
        :type minutesToDie: int
        :type minutesToTest: int
        :rtype: int
        �������ı�����һ��������˼�ı������⣬��������ͷ��ʱ��������һ�ֲ���8����������Կ��Եõ�buckets = pow(r + 1, n)
        """
        return int(math.ceil(math.log(buckets, 1 + minutesToTest / minutesToDie)))