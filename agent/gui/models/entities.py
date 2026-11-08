"""Instantanés immuables des données renvoyées par l'API C++."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Book:
    title: str
    author: str
    isbn: str
    available: bool
    borrower_id: str


@dataclass(frozen=True)
class Member:
    name: str
    user_id: str
    borrowed_isbns: tuple[str, ...]


@dataclass(frozen=True)
class Stats:
    total_books: int
    available_books: int
    loaned_books: int
    members: int


@dataclass(frozen=True)
class DataFile:
    name: str
    exists: bool
