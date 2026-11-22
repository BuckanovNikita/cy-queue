# cy-queue config

`cy-queue config` печатает настройки очереди, с которыми будет работать `cy-queue`. Запускайте её, чтобы проверить файл `queue.toml` и флаг `--root` до первого задания. Команда только читает настройки: каталоги не создаёт, worker и задания не запускает.

## Примеры

Проверить конфигурацию:

```bash
cy-queue config
```

Получить настройки в JSON:

```bash
cy-queue config --json
```

Проверить, какой каталог очереди (queue root) выберет флаг `--root`:

```bash
cy-queue --root /srv/cy-queue config
```

## Синтаксис и аргументы

```text
cy-queue [--root ROOT] config [-h] [--json]
```

| Аргумент | По умолчанию | Описание |
| --- | --- | --- |
| `--root ROOT` | `root` из `queue.toml` | Глобальный флаг: заменяет [каталог очереди (queue root)](../../GLOSSARY.md#queue-root) для этого вызова. Абсолютный путь. Пишется до подкоманды. |
| `--json` | выключен | Печатать настройки одним JSON-объектом. |
| `-h`, `--help` | — | Показать справку и выйти. |

## Как это работает

1. Команда находит файл конфигурации (порядок поиска — в [конфигурации](../configuration.md)) и читает раздел `[queue]`.
2. Если указан `--root`, он заменяет `root` из файла.
3. Команда проверяет, что пути абсолютные и, если каталоги уже существуют, что это каталоги, и проверяет файловую систему [каталога координации (coordination root)](../../GLOSSARY.md#coordination-root). Затем печатает результат.

Каталог очереди и каталог координации команда не создаёт: если их нет, `config` всё равно печатает настройки, а каталоги после этого так и не появляются. Другие подкоманды, например `list`, создают каталог очереди при первом запуске. Хост к каталогу координации команда не привязывает.

## Результат

Без `--json` команда печатает шесть строк:

```text
name: my-queue
root: /srv/cy-queue
coordination root: /var/lib/cy-queue
config path: /home/user/.config/clearml-yolo/queue.toml
root source: config
max used memory gib: 2.0
```

| Строка | Значение |
| --- | --- |
| `name` | Имя очереди, ключ `name`. |
| `root` | Каталог очереди: из `--root`, если он указан, иначе ключ `root`. |
| `coordination root` | Каталог координации, ключ `coordination_root`. |
| `config path` | Какой файл конфигурации прочитан. |
| `root source` | Откуда взят `root`: `config` — из файла, `--root` — из флага. |
| `max used memory gib` | [Порог занятой памяти (memory admission threshold)](../../GLOSSARY.md#memory-admission-threshold), ключ `max_used_memory_gib`. |

Пути печатаются в абсолютном виде и как есть, и в тексте, и в `--json`: их можно скопировать. В текстовом выводе только `name` проходит через замены текстовых полей (см. [формат JSON](../formats/json.md)); например, 64-символьный шестнадцатеричный токен в имени печатается как `<redacted>`. Сообщения об ошибках (`cy-queue: ...`) проходят через эти замены, как и у других подкоманд.

С `--json` команда печатает объект с ключами `name`, `root`, `coordination_root`, `config_path`, `root_source` и `max_used_memory_gib` (см. [формат JSON](../formats/json.md)).

### Флаг `--root`

`--root` — глобальный флаг: его принимают все подкоманды, и он стоит до имени подкоманды (`cy-queue --root /srv/cy-queue list`). После имени подкоманды флаг не принимается: `cy-queue config --root /srv/cy-queue` завершается с кодом `2` и сообщением `unrecognized arguments`. С ним `root source` равен `--root`:

```text
$ cy-queue --root /srv/cy-queue config
root: /srv/cy-queue
root source: --root
```

Остальные строки не меняются. Каталог координации флаг не заменяет. Подробности и связь с `CY_QUEUE_ROOT` — в [конфигурации](../configuration.md).

### Коды завершения

| Код | Когда |
| --- | --- |
| `0` | Настройки прочитаны и напечатаны. |
| `1` | Конфигурация отсутствует или неверна, или `--root` задан относительным путём; сообщение начинается с `cy-queue:`. |
| `2` | Ошибка аргументов командной строки, например `--root` после имени подкоманды. |

## Частые ошибки

Ошибки печатаются в stderr одной строкой вида:

```text
cy-queue: Queue configuration is missing: /home/user/.config/clearml-yolo/queue.toml. ...
cy-queue: Invalid queue configuration: expected [queue] with name, root and coordination_root; ...
cy-queue: --root must be an absolute path
```

`--root must be an absolute path` — в `--root` указан относительный путь. Укажите абсолютный.

Полный список сообщений, их причины и ключи — в [конфигурации](../configuration.md).

## См. также

- [Конфигурация](../configuration.md) — ключи `queue.toml` и переменные окружения.
- [Подготовка хоста](../setup.md).
- [Формат JSON](../formats/json.md).
- [`cy-queue submit`](submit.md).
