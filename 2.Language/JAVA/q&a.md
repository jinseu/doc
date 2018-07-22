## 其他问题

### ibatis $与#号的区别

```
1. #是把传入的数据当作字符串，如#field#传入的是id,则sql语句生成是这样，order by "id",这当然会报错．． 

2. $传入的数据直接生成在sql里，如$field$传入的是id,则sql语句生成是这样，order by id, 这就对了． 如：

    <</SPAN>isNotNull property="orderBy"> order by $orderBy$ 
        <</SPAN>isNotNull property="descOrAsc"> $descOrAsc$ </</SPAN>isNotNull>
    </</SPAN>isNotNull>
 
3. `#`方式能够很大程度防止sql注入． 

4. $方式一般用于传入数据库对象．例如传入表名. 

5. 一般能用#的就别用$.
```
http://www.cnblogs.com/google4y/p/3556357.html