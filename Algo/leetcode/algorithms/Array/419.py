# ��һ�ַ���Ӧ����ͨ��DFS���������������Ļ�������ҪM*N�Ŀռ�������Ƿ��������
#��һ�ַ���������ʾ���������������ַ��������ܱ������Ҵ�������
class Solution(object):
    def countBattleships(self, board):
        """
        :type board: List[List[str]]
        :rtype: int
        """
        m = len(board)
        n = len(board[0])
        if m == 0 or n == 0:
            return 0
        ship = 0
        i = 0
        while i < m:
            j = 0
            while j < n:
                if board[i][j] == '.' or (i > 0 and board[i - 1][j] == 'X') or (j > 0 and board[i][j - 1] == 'X'):
                    j += 1
                    continue
                ship += 1
                j += 1
            i += 1
        return ship



class Solution(object):
    def countBattleships(self, board):
        """
        :type board: List[List[str]]
        :rtype: int
        """
        m = len(board)
        n = len(board[0])
        if m == 0 or n == 0:
            return 0
        ship = 0
        i = 0
        while i < m:
            j = 0
            while j < n:
                if board[i][j] == '.':
                    j += 1
                    continue
                elif (i > 0 and board[i - 1][j] == 'X') and (j > 0 and board[i][j - 1] == 'X'):
                    ship -= 1
                    j += 1
                    continue
                elif (i > 0 and board[i - 1][j] == 'X') or (j > 0 and board[i][j - 1] == 'X'):
                    j += 1
                    continue
                
                ship += 1
                j += 1
            i += 1
        return ship