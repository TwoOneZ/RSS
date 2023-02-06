import re
from typing import Any, List, Optional

from bs4 import BeautifulSoup

from .models import RSSFeed


class Parser:
    """Парсер для rss файлов."""

    def __init__(self, xml: str, limit=None):
        self.xml = xml
        self.limit = limit

        self.raw_data = None
        self.rss = None

    @staticmethod
    def _check_atom(soup: BeautifulSoup):
        if soup.feed:
            raise NotImplementedError("Фид ATOM в настоящее время не поддерживается")

    @classmethod
    def get_soup(cls, xml: str, parser: str = "xml") -> BeautifulSoup:
        """
        Получить объект BeautifulSoup с указанным парсером.

        :param xml: содержимое xml
        :param parser: Тип парсера. По умолчанию xml
        :return: Объект BeautifulSoup
        """
        soup = BeautifulSoup(xml, parser)
        cls._check_atom(soup)
        return soup

    @staticmethod
    def check_none(
        item: object,
        default: str,
        item_dict: Optional[str] = None,
        default_dict: Optional[str] = None,
    ) -> Any:
        """
        Проверьте, является ли item_dict в элементе None, иначе возвращает значение default_dict по умолчанию.

        :param item: Первый объект.
        :param default: Объект по умолчанию.
        :param item_dict: Словарь элементов.
        :param default_dict: Словарь по умолчанию.
        :return: Конечный объект (не None).
        """
        if item:
            return item[item_dict]
        else:
            if default_dict:
                return default[default_dict]
            else:
                return default

    @staticmethod
    def get_text(item: object, attribute: str) -> str:
        """
        Возвращает текстовую информацию об атрибуте объекта.

        Если его нет, будет возвращена пустая строка.
        :param item: Объект с атрибутом
        :param attribute: Атрибут, который имеет атрибут 'text'
        :return: Строка текста указанного атрибута
        """
        return getattr(getattr(item, attribute, ""), "text", "")

    def parse(self, entries: Optional[List[str]] = List) -> RSSFeed:
        """
        Разобрать rss и каждый элемент ленты.

        Отсутствующие атрибуты будут заменены пустой строкой.
        информация о дополнительных записях хранится в словаре
        под атрибутом «другое» каждого элемента.

        :param entry: необязательный список дополнительных RSS-тегов, которые можно восстановить.
        с каждого предмета
        :return: RSS-канал, описывающий rss-информацию
        """
        main_soup = self.get_soup(self.xml)

        self.raw_data = {
            "title": main_soup.title.text,
            "version": main_soup.rss.get("version"),
            "language": getattr(main_soup.language, "text", ""),
            "description": getattr(main_soup.description, "text", ""),
            "feed": [],
        }

        items = main_soup.findAll("item")

        if self.limit is not None:
            items = items[: self.limit]

        for item in items:
            # Использование html.parser вместо lxml, потому что lxml не может разобрать <ссылку>
            description_soup = self.get_soup(
                self.get_text(item, "description"), "html.parser"
            )

            item_dict = {
                "title": self.get_text(item, "title"),
                "link": self.get_text(item, "link"),
                "publish_date": self.get_text(item, "pubDate"),
                "category": self.get_text(item, "category"),
                "description": getattr(description_soup, "text", ""),
                "description_links": [
                    anchor.get("href")
                    for anchor in description_soup.findAll("a")
                    # оператор if, чтобы избежать неверных значений в списке
                    if anchor.get("href")
                ],
                "description_images": [
                    {"alt": image.get("alt", ""), "source": image.get("src")}
                    for image in description_soup.findAll("img")
                ],
            }

            try:
                # Добавить пользовательские записи
                item_dict.update({"other": {}})
                for entrie in entries:
                    value = self.get_text(item, entrie)
                    value = re.sub(f"</?{entrie}>", "", value)
                    item_dict["other"].update({entrie: value})

                item_dict.update(
                    {
                        "enclosure": {
                            "content": "",
                            "attrs": {
                                "url": item.enclosure["url"],
                                "length": item.enclosure["length"],
                                "type": item.enclosure["type"],
                            },
                        },
                        "itunes": {
                            "content": "",
                            "attrs": {
                                "href": self.check_none(
                                    item.find("itunes:image"),
                                    main_soup.find("itunes:image"),
                                    "href",
                                    "href",
                                )
                            },
                        },
                    }
                )
            except (TypeError, KeyError, AttributeError):
                pass

            self.raw_data["feed"].append(item_dict)

        return RSSFeed(**self.raw_data)
