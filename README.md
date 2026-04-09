# otchet-compose

CLI-генератор отчётов по лабораторным работам в формате DOCX.

Формирует документ по YAML-конфигурации: ГОСТ-оформление (A4, Times New Roman 14 пт, полуторный интервал, поля 3 см слева), автоматическое оглавление, нумерация страниц в нижнем колонтитуле.

## Требования

- Python 3.10+
- зависимости устанавливаются автоматически при установке пакета

## Установка

```bash
pip install -e .
```

## Использование

```bash
otchet-compose gen -f path/to/config.yml   # указать файл явно
otchet-compose gen                          # ищет ./otchet-compose.yml
```

Результат сохраняется в путь, указанный в `document.output`; родительские директории создаются автоматически.

## Формат конфигурации

```yaml
version: 1

document:
  output: "./build/report.docx"
  reserve_title_page: true   # оставить пустую первую страницу под титульник
  toc: true                  # вставить автоматическое оглавление

content:
  - type: heading
    text: "Цель работы"
    level: 1
    structural: true          # ALL-CAPS + разрыв страницы перед заголовком

  - type: paragraph
    text: >
      Текст абзаца. Используй folded scalar (>) чтобы не было
      лишних переносов строк в Word.

  - type: figure
    caption: "Подпись рисунка"   # номер добавляется автоматически
    path: "./images/foo.png"      # path можно не указывать — будет placeholder

  - type: list
    style: bullet    # bullet — маркированный (–), numeric — нумерованный (1), 2), …)
    items:
      - "Первый элемент"
      - "Второй элемент"

  - type: table
    caption: "Подпись таблицы"   # номер добавляется автоматически
    headers:
      - "Столбец 1"
      - "Столбец 2"
    rows:
      - ["Значение A", "Значение B"]
      - ["Значение C", "Значение D"]
```

## Поддерживаемые типы блоков

| Тип | Описание |
|---|---|
| `heading` | Заголовок уровня 1–3. `structural: true` → ALL-CAPS, разрыв страницы |
| `paragraph` | Абзац основного текста с отступом 1.25 см |
| `figure` | Рисунок с автонумерацией. Без `path` — placeholder-таблица |
| `list` | Маркированный (`bullet`) или нумерованный (`numeric`) список |
| `table` | Таблица с заголовком строки. Подпись — над таблицей, по правому краю |

## Структура проекта

```
src/otchet_compose/
  cli.py                      — точка входа (argparse, подкоманда gen)
  config.py                   — загрузка и валидация YAML
  generator/
    build.py                  — оркестратор: создаёт Document, вызывает блоки, сохраняет файл
    styles.py                 — ГОСТ-стили параграфов (загружаются из styles.json)
    styles.json               — определения стилей (можно переопределить через ~/.otchet-compose/styles.json)
    page.py                   — размер страницы, поля, нижний колонтитул с номером страницы
    fields.py                 — низкоуровневые OOXML-хелперы (поля Word, шрифты)
    blocks/
      __init__.py             — реестр REGISTRY: тип → обработчик
      _base.py                — RenderContext, протокол BlockHandler
      heading.py              — обработчик heading
      paragraph.py            — обработчик paragraph
      figure.py               — обработчик figure
      list.py                 — обработчик list
      table.py                — обработчик table
```

## Переопределение стилей

Чтобы изменить шрифты, отступы или интервалы без правки пакета, создай файл `~/.otchet-compose/styles.json` — он будет иметь приоритет над встроенным.

## Добавление нового типа блока

1. Создай `src/otchet_compose/generator/blocks/<type>.py` с методами `validate` и `render`.
2. Добавь одну запись в `REGISTRY` в `blocks/__init__.py`.

Больше ничего менять не нужно.

## Справочные файлы

- `doc/otchet-compose.llm.ref.yml` — полный аннотированный YAML для промптов LLM.
- `doc/prompt.txt` — системный промпт для генерации конфига из текста лабораторной работы.
- `examples/otchet-compose.yml` — рабочий пример конфигурации.
