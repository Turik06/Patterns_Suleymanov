import time
import math


cal_ID = 0


class MonthlyCalendar:
    """
    Класс для формирования HTML-представления месячного календаря.
    Поддерживает локализацию (ru, en, de), подсветку выходных и праздничных дней,
    а также экспорт готового календаря в HTML-файл.
    """

    # Конфигурация поддерживаемых языков
    LANGUAGES = {
        'ru': {
            'weekdays': ('Сб', 'Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт'),
            'months': ('Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                       'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'),
            'error': ('Год должен быть в диапазоне 1 - 3999!', 'Месяц должен быть в диапазоне 1 - 12!'),
            'offset': 2,  # Неделя начинается с понедельника
            'holidays': {
                1: [(1, 8, 'Новогодние каникулы и Рождество')],
                2: [(23, 23, 'День защитника Отечества')],
                3: [(8, 8, 'Международный женский день')],
                5: [(1, 1, 'Праздник Весны и Труда'), (9, 9, 'День Победы')],
                6: [(12, 12, 'День России')],
                11: [(4, 4, 'День народного единства')],
            }
        },
        'en': {
            'weekdays': ('Sat', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri'),
            'months': ('January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'),
            'error': ('Year must be 1 - 3999!', 'Month must be 1 - 12!'),
            'offset': 1,  # Неделя начинается с воскресенья
            'holidays': {
                1: [(1, 1, "New Year's Day")],
                7: [(4, 4, 'Independence Day')],
                11: [(11, 11, 'Veterans Day')],
                12: [(25, 25, 'Christmas Day'), (26, 26, 'Boxing Day')],
            }
        },
        'de': {
            'weekdays': ('Sa', 'So', 'Mo', 'Di', 'Mi', 'Do', 'Fr'),
            'months': ('Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                       'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'),
            'error': ('Jahr muss zwischen 1 und 3999 liegen!', 'Monat muss между 1 und 12 liegen!'),
            'offset': 1,  # Неделя начинается с воскресенья
            'holidays': {
                1: [(1, 1, 'Neujahr')],
                5: [(1, 1, 'Tag der Arbeit')],
                10: [(3, 3, 'Tag der Deutschen Einheit')],
                12: [(25, 25, '1. Weihnachtstag'), (26, 26, '2. Weihnachtstag')],
            }
        }
    }

    __size = 0

    def __init__(self, year = None, month = None, lang = 'ru'):
        """
        Инициализация календаря.
        :param year: Год (1-3999)
        :param month: Месяц (1-12)
        :param lang: Язык календаря ('ru', 'en', 'de'). По умолчанию 'ru'.
        """
        self.tFontFace = 'Arial, Helvetica'
        self.tFontSize = 12                
        self.tFontColor = '#FFFFFF'         
        self.tBGColor = '#304B90'          

        self.hFontFace = 'Arial, Helvetica' 
        self.hFontSize = 10                 
        self.hFontColor = '#FFFFFF'        
        self.hBGColor = '#304B90'          

        self.dFontFace = 'Arial, Helvetica' 
        self.dFontSize = 12                 
        self.dFontColor = '#000000'         
        self.dBGColor = '#FFFFFF'           

        self.wFontFace = 'Arial, Helvetica' 
        self.wFontSize = 10                 
        self.wFontColor = '#FFFFFF'         
        self.wBGColor = '#304B90'           

        self.saFontColor = '#FF0000'       
        self.saBGColor = '#FFF0F0'          

        self.suFontColor = '#FF0000'        
        self.suBGColor = '#FFF0F0'          

        self.holidayFontColor = '#0000D0'
        self.holidayBGColor = '#E6F0FA'

        self.tdBorderColor = 'red'      
        self.borderColor = '#304B90'        
        self.hilightColor = '#FFFF00'       

        self.link = ''                      
        self.weekNumbers = 0

        self.weekdays = ()
        self.months = ()
        self.error = ()
        self.offset = 2

        self.__mDays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        if year is None and month is None:
            year = time.localtime().tm_year
            month = time.localtime().tm_mon
        elif year is None and month is not None:
            year = time.localtime().tm_year
        elif month is None:
            month = 1

        self.year = int(year)
        self.month = int(month)
        self.specDays = {}

        self.set_language(lang)

    def set_language(self, lang = 'ru'):
        """
        Настройка языка календаря.
        Поддерживаются: 'ru' (по умолчанию), 'en', 'de'.
        """
        if lang not in self.LANGUAGES:
            lang = 'ru'
        self.lang = lang
        cfg = self.LANGUAGES[lang]
        self.weekdays = cfg['weekdays']
        self.months = cfg['months']
        self.error = cfg['error']
        self.offset = cfg['offset']
        self.load_holidays()

    def load_holidays(self):
        """
        Загружает предопределенные праздники для выбранного языка и текущего месяца.
        """
        self.specDays = {}
        lang_data = self.LANGUAGES.get(self.lang, self.LANGUAGES['ru'])
        month_holidays = lang_data.get('holidays', {}).get(self.month, [])
        for start, end, title in month_holidays:
            self.viewEvent(start, end, self.holidayBGColor, title, link='', fontColor=self.holidayFontColor)

    def set_styles(self):
        """Генерация CSS-стилей для таблицы календаря."""
        globals()['cal_ID'] += 1
        cid = str(globals()['cal_ID'])
        html = '<style> .cssTitle' + cid + ' { '
        if self.tFontFace: html += 'font-family: ' + self.tFontFace + '; '
        if self.tFontSize: html += 'font-size: ' + str(self.tFontSize) + 'px; '
        if self.tFontColor: html += 'color: ' + self.tFontColor + '; '
        if self.tBGColor: html += 'background-color: ' + self.tBGColor + '; '
        html += '} .cssHeading' + cid + ' { '
        if self.hFontFace: html += 'font-family: ' + self.hFontFace + '; '
        if self.hFontSize: html += 'font-size: ' + str(self.hFontSize) + 'px; '
        if self.hFontColor: html += 'color: ' + self.hFontColor + '; '
        if self.hBGColor: html += 'background-color: ' + self.hBGColor + '; '
        html += '} .cssDays' + cid + ' { '
        if self.dFontFace: html += 'font-family: ' + self.dFontFace + '; '
        if self.dFontSize: html += 'font-size: ' + str(self.dFontSize) + 'px; '
        if self.dFontColor: html += 'color: ' + self.dFontColor + '; '
        if self.dBGColor: html += 'background-color: ' + self.dBGColor + '; '
        html += '} .cssWeeks' + cid + ' { '
        if self.wFontFace: html += 'font-family: ' + self.wFontFace + '; '
        if self.wFontSize: html += 'font-size: ' + str(self.wFontSize) + 'px; '
        if self.wFontColor: html += 'color: ' + self.wFontColor + '; '
        if self.wBGColor: html += 'background-color: ' + self.wBGColor + '; '
        html += '} .cssSaturdays' + cid + ' { '
        if self.dFontFace: html += 'font-family: ' + self.dFontFace + '; '
        if self.dFontSize: html += 'font-size: ' + str(self.dFontSize) + 'px; '
        if self.saFontColor: html += 'color: ' + self.saFontColor + '; '
        if self.saBGColor: html += 'background-color: ' + self.saBGColor + '; '
        html += '} .cssSundays' + cid + ' { '
        if self.dFontFace: html += 'font-family: ' + self.dFontFace + '; '
        if self.dFontSize: html += 'font-size: ' + str(self.dFontSize) + 'px; '
        if self.suFontColor: html += 'color: ' + self.suFontColor + '; '
        if self.suBGColor: html += 'background-color: ' + self.suBGColor + '; '
        html += '} .cssHilight' + cid + ' { '
        if self.dFontFace: html += 'font-family: ' + self.dFontFace + '; '
        if self.dFontSize: html += 'font-size: ' + str(self.dFontSize) + 'px; '
        if self.dFontColor: html += 'color: ' + self.dFontColor + '; '
        if self.hilightColor: html += 'background-color: ' + self.hilightColor + '; '
        html += 'cursor: default; '
        html += '} </style>'
        return html

    def leap_year(self, year):
        """Проверка, является ли год високосным."""
        return not (year % 4) and (year < 1582 or year % 100 or not (year % 400))

    def get_weekday(self, year, days):
        """Вычисление дня недели первого дня месяца."""
        a = days
        if year: a += (year - 1) * 365
        for i in range(1, year):
            if self.leap_year(i): a += 1
        if year > 1582 or (year == 1582 and days >= 277): a -= 10
        if a: a = (a - self.offset) % 7
        elif self.offset: a += 7 - self.offset
        return a

    def get_week(self, year, days):
        """Вычисление номера недели."""
        firstWDay = self.get_weekday(year, 0)
        return int(math.floor((days + firstWDay) / 7) + (firstWDay <= 3))

    def table_cell(self, content, cls, date = '', style = ''):
        """Формирование одной ячейки таблицы календаря."""
        size = int(round(self.__size * 1.5))
        html = '<td align=center width=' + str(size) + ' class="' + cls + '"'

        if content != '&nbsp;' and cls.lower().find('day') != -1:
            link = self.link

            if str(content) in self.specDays:
                spec = self.specDays[str(content)]
                if spec[0]:
                    style += 'background-color:' + spec[0] + ';'
                if len(spec) > 3 and spec[3]:
                    style += 'color:' + spec[3] + ';'
                if spec[1]:
                    html += ' title="' + spec[1] + '"'
                if len(spec) > 2 and spec[2]:
                    link = spec[2]
                    style += 'cursor:pointer;'
                else:
                    link = 'brak'
                    style += 'cursor:pointer;'

            cid = str(globals()['cal_ID'])
            if link == 'brak':
                html += ' onMouseOver="this.className=\'cssHilight' + cid + '\'"'
                html += ' onMouseOut="this.className=\'' + cls + '\'"'
                html += ' onClick="document.location.href=\'' + '?date=' + date + '\'"'

            if link and link != 'brak':
                html += ' onMouseOver="this.className=\'cssHilight' + cid + '\'"'
                html += ' onMouseOut="this.className=\'' + cls + '\'"'
                html += ' onClick="document.location.href=\'' + link + '?date=' + date + '\'"'

        if style: html += ' style="' + style + '"'
        html += '>' + str(content) + '</td>'
        return html

    def table_head(self, content):
        """Формирование строки заголовка таблицы (месяц, год и названия дней недели)."""
        cols = self.weekNumbers and '8' or '7'
        cid = str(globals()['cal_ID'])
        html = '<tr><td colspan=' + cols + ' class="cssTitle' + cid + '" align=center><b>' + \
               content + '</b></td></tr><tr>'
        for i in range(len(self.weekdays)):
            ind = (i + self.offset) % 7
            wDay = self.weekdays[ind]
            html += self.table_cell(wDay, 'cssHeading' + cid)
        if self.weekNumbers: html += self.table_cell('&nbsp;', 'cssHeading' + cid)
        html += '</tr>'
        return html

    def viewEvent(self, start, end, color, title, link = '', fontColor = '#0000D0'):
        """
        Регистрация специального дня или диапазона дней (праздника/события).
        :param start: Начальный день
        :param end: Конечный день
        :param color: Цвет фона ячейки
        :param title: Всплывающая подсказка
        :param link: URL перехода при клике
        :param fontColor: Цвет шрифта (по умолчанию #0000D0 для праздников)
        """
        if start > end: return
        if start < 1 or start > 31: return
        if end < 1 or end > 31: return
        while start <= end:
            self.specDays[str(start)] = [color, title, link, fontColor]
            start += 1

    def create(self):
        """Генерация HTML-фрагмента таблицы календаря."""
        self.__size = (self.hFontSize > self.dFontSize) and self.hFontSize or self.dFontSize
        if self.wFontSize > self.__size: self.__size = self.wFontSize

        date = time.strftime('%Y-%m-%d', time.localtime())
        (curYear, curMonth, curDay) = [int(v) for v in date.split('-')]

        if self.year < 1 or self.year > 3999: html = '<b>' + self.error[0] + '</b>'
        elif self.month < 1 or self.month > 12: html = '<b>' + self.error[1] + '</b>'
        else:
            self.__mDays[1] = 29 if self.leap_year(self.year) else 28
            days = 0
            for i in range(self.month - 1): days += self.__mDays[i]

            start = self.get_weekday(self.year, days)
            stop = self.__mDays[self.month - 1]

            html = self.set_styles()
            html += '<table border=1 cellspacing=0 cellpadding=0><tr>'
            html += '<td' + (self.borderColor and ' bgcolor=' + self.borderColor) + '>'
            html += '<table border=0 cellspacing=1 cellpadding=3>'
            title = self.months[self.month - 1] + ' ' + str(self.year)
            html += self.table_head(title)
            daycount = 1

            if self.year == curYear and self.month == curMonth: inThisMonth = 1
            else: inThisMonth = 0

            if self.weekNumbers: weekNr = self.get_week(self.year, days)

            while daycount <= stop:
                html += '<tr>'
                wdays = 0

                for i in range(len(self.weekdays)):
                    ind = (i + self.offset) % 7
                    if ind == 0: cls = 'cssSaturdays'
                    elif ind == 1: cls = 'cssSundays'
                    else: cls = 'cssDays'

                    style = ''
                    date = "%s-%s-%s" % (self.year, self.month, daycount)

                    if (daycount == 1 and i < start) or daycount > stop: content = '&nbsp;'
                    else:
                        content = str(daycount)
                        if inThisMonth and daycount == curDay:
                            style = 'padding:0px;border:3px solid ' + self.tdBorderColor + ';'
                        elif self.year == 1582 and self.month == 10 and daycount == 4: daycount = 14
                        daycount += 1
                        wdays += 1

                    cid = str(globals()['cal_ID'])
                    html += self.table_cell(content, cls + cid, date, style)

                if self.weekNumbers:
                    if not weekNr:
                        if self.year == 1: content = '&nbsp;'
                        elif self.year == 1583: content = '52'
                        else: content = str(self.get_week(self.year - 1, 365))
                    elif self.month == 12 and weekNr >= 52 and wdays < 4: content = '1'
                    else: content = str(weekNr)

                    cid = str(globals()['cal_ID'])
                    html += self.table_cell(content, 'cssWeeks' + cid)
                    weekNr += 1

                html += '</tr>'
            html += '</table></td></tr></table>'
        return html

    def save_to_html(self, filename = None):
        """
        Сохранение календаря в HTML-файл.
        :param filename: Произвольное имя файла, расширение строго .html
        """
        if filename is None:
            filename = f"calendar_{self.year}_{self.month}.html"

        if not filename.lower().endswith('.html'):
            raise ValueError("Расширение файла должно быть строго .html!")

        full_html = (
            "<!DOCTYPE html>\n"
            f"<html lang=\"{self.lang}\">\n"
            "<head>\n"
            "    <meta charset=\"utf-8\">\n"
            f"    <title>{self.months[self.month - 1]} {self.year}</title>\n"
            "</head>\n"
            "<body>\n"
            f"{self.create()}\n"
            "</body>\n"
            "</html>"
        )
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(full_html)
        return filename


def main():
    """
    Интерактивный запуск генератора календаря для Заказчика.
    """
    print("=== Генератор календаря ===")

    lang = input("Выберите язык (ru - русский, en - английский, de - немецкий) [ru]: ").strip().lower()
    if not lang:
        lang = 'ru'
    elif lang not in MonthlyCalendar.LANGUAGES:
        print("Неизвестный язык. Будет использован русский (ru).")
        lang = 'ru'

    cur_year = time.localtime().tm_year
    year_str = input(f"Введите год (1-3999) [{cur_year}]: ").strip()
    year = int(year_str) if year_str else cur_year

    cur_month = time.localtime().tm_mon
    month_str = input(f"Введите месяц (1-12) [{cur_month}]: ").strip()
    month = int(month_str) if month_str else cur_month

    while True:
        filename = input("Введите имя файла для выгрузки (расширение строго .html): ").strip()
        if not filename:
            filename = f"calendar_{year}_{month}.html"
            print(f"Имя файла не введено. Использовано по умолчанию: {filename}")
            break
        if filename.lower().endswith('.html'):
            break
        print("Ошибка: расширение файла должно быть строго .html! Попробуйте снова.")

    cal = MonthlyCalendar(year=year, month=month, lang=lang)
    saved_file = cal.save_to_html(filename)
    print(f"Календарь успешно сохранен в файл: {saved_file}")


if __name__ == '__main__':
    main()
