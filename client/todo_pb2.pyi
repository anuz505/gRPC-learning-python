import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Todo(_message.Message):
    __slots__ = ("id", "title", "description", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    description: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetTodosRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetTodosResponse(_message.Message):
    __slots__ = ("todos",)
    TODOS_FIELD_NUMBER: _ClassVar[int]
    todos: _containers.RepeatedCompositeFieldContainer[Todo]
    def __init__(self, todos: _Optional[_Iterable[_Union[Todo, _Mapping]]] = ...) -> None: ...

class GetTodoByIdRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetTodoByIdResponse(_message.Message):
    __slots__ = ("todo",)
    TODO_FIELD_NUMBER: _ClassVar[int]
    todo: Todo
    def __init__(self, todo: _Optional[_Union[Todo, _Mapping]] = ...) -> None: ...

class CreateTodoRequest(_message.Message):
    __slots__ = ("todo",)
    TODO_FIELD_NUMBER: _ClassVar[int]
    todo: Todo
    def __init__(self, todo: _Optional[_Union[Todo, _Mapping]] = ...) -> None: ...

class CreateTodoResponse(_message.Message):
    __slots__ = ("todo",)
    TODO_FIELD_NUMBER: _ClassVar[int]
    todo: Todo
    def __init__(self, todo: _Optional[_Union[Todo, _Mapping]] = ...) -> None: ...

class UpdateTodoRequest(_message.Message):
    __slots__ = ("todo",)
    TODO_FIELD_NUMBER: _ClassVar[int]
    todo: Todo
    def __init__(self, todo: _Optional[_Union[Todo, _Mapping]] = ...) -> None: ...

class UpdateTodoResponse(_message.Message):
    __slots__ = ("todo",)
    TODO_FIELD_NUMBER: _ClassVar[int]
    todo: Todo
    def __init__(self, todo: _Optional[_Union[Todo, _Mapping]] = ...) -> None: ...

class DeleteTodoRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteTodoResponse(_message.Message):
    __slots__ = ("todo",)
    TODO_FIELD_NUMBER: _ClassVar[int]
    todo: Todo
    def __init__(self, todo: _Optional[_Union[Todo, _Mapping]] = ...) -> None: ...
