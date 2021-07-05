def check_date(y, m, d):
    months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
    for index in range(len(months)):
        if m == months[index]:
            m = index