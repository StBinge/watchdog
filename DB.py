from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class TaskData(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, Sequence('task_id_seq'), primary_key=True)
    name = Column(String)
    cmd = Column(String)
    cron = Column(String)

    def __repr__(self):
        return f"Task(id={self.id}, cmd='{self.cmd}', cron='{self.cron}')"


class EnvItem(Base):
    __tablename__ = 'envs'
    key = Column(String, Sequence('env_key_seq'), primary_key=True)
    value = Column(String)

    def __repr__(self):
        return f"Env(key={self.key}, val='{self.value}')"


class Database:
    def __init__(self) -> None:
        self.engine = create_engine('sqlite:///task.db')
        Base.metadata.create_all(self.engine)

    def __enter__(self):
        # 创建一个会话
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        self.session = None
        # if exc_type:
        #     raise exc_type(exc_val)

    def add_task(self, name, cmd, cron):
        new_task = TaskData(name=name, cmd=cmd, cron=cron)
        with self as session:
            session.add(new_task)
            session.commit()
            return session.query(TaskData).filter_by(id=new_task.id).first()

    def get_all_tasks(self) -> list[TaskData]:
        with self as session:
            return session.query(TaskData).all()

    def get_task_by_id(self, id):
        with self as session:
            return session.query(TaskData).filter_by(id=id).first()

    def update_task(self, id, name=None, cmd=None, cron=None):
        with self as session:
            task = session.query(TaskData).filter_by(id=id).first()
            if not task:
                raise Exception('task not found')
            changed = False
            if name and name != task.name:
                task.name = name
                changed = True
            if cmd and cmd != task.cmd:
                task.cmd = cmd
                changed = True
            if cron and cron != task.cron:
                task.cron = cron
                changed = True
            if changed:
                session.commit()
                return task
            else:
                return None

    def delete_task(self, id):
        with self as session:
            session.query(TaskData).filter_by(id=id).delete()
            session.commit()

    def clean_all_tasks(self):
        with self as session:
            session.query(TaskData).delete()
            session.commit()

    def add_env(self, key, val):
        item = EnvItem(key=key, value=val)
        with self as session:
            session.add(item)
            session.commit()
            return {'key':key,'value':val}

    def delete_env(self, key):
        with self as s:
            s.query(EnvItem).filter_by(key=key).delete()
            s.commit()
            return key

    def add_or_update_env(self, key, val):
        with self as session:
            item = session.query(EnvItem).filter_by(key=key).first()
            if not item:
                item = EnvItem(key=key, value=val)
                session.add(item)
                session.commit()
            elif item.value != val:
                item.value = val
                session.commit()
            return {'key':key,'value':val}


    def get_all_envs(self) -> list[EnvItem]:
        with self as session:
            return session.query(EnvItem).all()

    def clean_all_envs(self):
        with self as session:
            session.query(EnvItem()).delete()
            session.commit()


if __name__ == '__main__':
    db = Database()
    # t = db.add_task('echo 3', '* * * * * ')
    # print(t)
    # db.delete_task(1)
    # db.clean_all_tasks()
    # db.update_task(3,cmd='ls')
    tasks = db.get_all_tasks()
    print(tasks)
