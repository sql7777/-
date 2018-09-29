tname='testtable'
field={'id':'INT PRIMARY KEY NOT NULL','1':'INT','2':'TEXT'}
data={'id':0,'1':100,'2':'ttttt'}
'''
sqlstr="create table {0} (".format(tname)
print(sqlstr)
for k,v in field.items():
    stemp=k+' '+v
    sqlstr+=(stemp+',')
print(sqlstr)
sqlstr=sqlstr.rstrip(',')
print(sqlstr)
sqlstr+=')'
print(sqlstr)

sqlstrIn="INSERT INTO {0} (".format(tname)
sqlstrV="VALUES ("
for k,v in field.items():
    sqlstrIn+=(k+",")
    tv=data[k]
    if isinstance(tv,str):
        sqlstrV+=("\""+tv+"\""+",")
    else:
        sqlstrV+=(str(tv)+",")

sqlstrIn=sqlstrIn.rstrip(',')
sqlstrIn+=')'
sqlstrV=sqlstrV.rstrip(',')
sqlstrV+=')'

sqlstr1=sqlstrIn+sqlstrV
print(sqlstr1)
'''
kvindex={'id':0}
sqlstrIn="UPDATE {0} SET ".format(tname)
sqlstrV="VALUES ("
for k,v in field.items():
    tv=data[k]
    if isinstance(tv,str):
        sqlstrIn+=(k+" = "+"\""+tv+"\""+",")
    else:
        sqlstrIn+=(k+" = "+str(tv)+",")
                
sqlstrIn=sqlstrIn.rstrip(',')
sqlstrIn+=' '
print(sqlstrIn)
sqlstrV="WHERE "
for ki,vi in kvindex.items():
    if isinstance(vi,str):
        sqlstrV="{0} = \"{1}\"".format(ki,vi)
    else:
        sqlstrV="{0} = {1}".format(ki,str(vi))
sqlstr1=sqlstrIn+"WHERE "+sqlstrV
print(sqlstr1)
