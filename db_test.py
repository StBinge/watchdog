from DB import Database



db=Database()
ret=db.get_all_envs()
print(ret)