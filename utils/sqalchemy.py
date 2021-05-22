#   requirments :- sqlalchemy

from sqlalchemy import Table,orm


#   convert table object to dict
#   inherit to table models only
class DictModel:
    """
    > inherit this class to add _asdict() method to tables model \n
    > _addict() is used to convert result to dict
    """
    def _asdict(self):
        result = dict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result


#   convert view object to dict
#   inherit to view models only
class ViewDict():
    """
    > inherit this class to add _asdict() method to views model \n
    > _addict() is used to convert result to dict
    """
    def _asdict(self):
        res = dict()
        for i in self.cols:
            res.update({i:getattr(self, i)}) 
        return res


#   convert list of table/view object to dict list
def aslist(data):
    
    """
    convert list of table/view object to lict of dict
    """
    try:
        data = list(data)
        if data == [] or data == None:
            return []
        if hasattr(data[0],"_asdict"):
            return [ i._asdict() for i in data ]
        else:
            return [ dict(i) for i in data ]
    except Exception as e:
        return []