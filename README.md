# Russian POS Lemmatizer

## Использование

Запуск программы для ввода текста:

```bash
python main.py
```

Пример ввода:

```text
я хихикаю
```

Вывод:

```text
я{я=NI} хихикаю{хихикать=V?0.9}
```

Для оценки точности на корпусе UD:

```bash
python main.py --eval
```
