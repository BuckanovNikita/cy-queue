# Конфигурация

Эта страница описывает файл конфигурации (configuration) `queue.toml`, глобальный флаг `--root` и переменные окружения, которые меняют поведение `cy-queue`. Каждый пользователь хоста держит свой файл; без него не работает ни одна подкоманда, кроме `--help`. Как выбрать каталоги и подготовить хост, описано в [setup.md](setup.md).

## Где ищется файл

`cy-queue` берёт первый подходящий путь из списка:

1. `CY_QUEUE_CONFIG`, если переменная задана и не пуста. Путь должен быть абсолютным.
2. `$XDG_CONFIG_HOME/clearml-yolo/queue.toml`, если `XDG_CONFIG_HOME` задана и содержит абсолютный путь. Относительное значение пропускается.
3. `$HOME/.config/clearml-yolo/queue.toml`. Если `HOME` не задана, берётся домашний каталог учётной записи.

Файл не создаётся сам. Проверить, какой файл выбран и что в нём прочитано, можно командой [`cy-queue config`](commands/config.md):

```bash
cy-queue config
```

```text
name: my-queue
root: /srv/cy-queue
coordination root: /var/lib/cy-queue
config path: /home/user/.config/clearml-yolo/queue.toml
root source: config
max used memory gib: 2.0
```

## Раздел `[queue]`

Файл содержит один раздел `[queue]`:

```toml
[queue]
name = "my-queue"
root = "/srv/cy-queue"
coordination_root = "/var/lib/cy-queue"
max_used_memory_gib = 2.0
```

| Ключ | Тип | По умолчанию | Описание |
| --- | --- | --- | --- |
| `name` | строка | обязателен | Имя очереди (queue). Печатается в первой строке `list` и в журнале worker. Пробелы по краям отбрасываются; остаток должен быть непустым и состоять из печатаемых символов. |
| `root` | строка | обязателен | [Каталог очереди (queue root)](../GLOSSARY.md#queue-root): задания, их порядок и пометки архива. Абсолютный путь. Может лежать на NFS. Флаг `--root` заменяет его для одного вызова. |
| `coordination_root` | строка | обязателен | [Каталог координации (coordination root)](../GLOSSARY.md#coordination-root): резервы GPU и удержания на этом хосте. Абсолютный путь на поддерживаемой файловой системе, см. [setup.md](setup.md#каталог-координации). |
| `max_used_memory_gib` | число | `2.0` | [Порог занятой памяти (memory admission threshold)](../GLOSSARY.md#memory-admission-threshold) в GiB: GPU, на котором занято столько памяти или больше, не получает новое задание. Положительное конечное число; целое значение тоже принимается. |

Ограничения:

- В файле допустим только раздел `[queue]`, а в нём только эти четыре ключа. Лишний ключ или раздел, пропущенный обязательный ключ, значение не того типа (например, число вместо строки в `root`) и `max_used_memory_gib`, равный нулю, отрицательный, `inf` или `nan`, дают ошибку «Invalid queue configuration».
- `root` и `coordination_root` должны быть абсолютными путями. Символические ссылки в них раскрываются.
- Если путь уже существует, это должен быть каталог. Несуществующий каталог создаётся при первом обращении к очереди (не командой `config`).
- Файловая система `coordination_root` проверяется при каждом запуске, включая `config`.

Ключи читаются при каждом запуске `cy-queue`. Запущенный worker работает с теми значениями, которые прочитал при старте; после правки файла перезапустите его.

## Флаг `--root`

Глобальный флаг `--root PATH` пишется до подкоманды и заменяет `root` из файла для одного вызова:

```bash
cy-queue --root /srv/cy-queue list
```

- Путь должен быть абсолютным.
- Флаг не заменяет файл конфигурации: файл всё равно должен существовать и быть полным, а `name`, `coordination_root` и `max_used_memory_gib` берутся из него.
- `cy-queue config` показывает выбранный путь и `root source: --root`.

Подробнее о флаге на практике — в [commands/config.md](commands/config.md).

## Устаревшая переменная `CY_QUEUE_ROOT`

`CY_QUEUE_ROOT` больше не выбирает каталог очереди. Если она задана, её значение (абсолютный путь) должно совпадать с выбранным каталогом очереди (`root` или `--root`), иначе любая подкоманда завершается ошибкой:

```text
cy-queue: CY_QUEUE_ROOT conflicts with the selected queue root; remove the legacy variable and configure CY_QUEUE_CONFIG or --root
```

Уберите переменную из окружения (`unset CY_QUEUE_ROOT`) и задайте каталог в `queue.toml` или флагом `--root`.

## Переменные окружения

Переменные, которые вы задаёте сами:

| Переменная | Что делает |
| --- | --- |
| `CY_QUEUE_CONFIG` | Абсолютный путь к файлу конфигурации вместо пути по умолчанию. |
| `XDG_CONFIG_HOME` | Каталог, в котором ищется `clearml-yolo/queue.toml`, если `CY_QUEUE_CONFIG` не задана. |
| `HOME` | Домашний каталог для пути по умолчанию `~/.config/clearml-yolo/queue.toml`. |
| `CY_QUEUE_ROOT` | Устаревшая; допустима только при совпадении с выбранным каталогом очереди (см. выше). |
| `CY_HOME` | Рабочий каталог (project), который `submit` записывает в задание; без неё берётся текущий каталог. В этом каталоге задание пишет журнал и выходные файлы, см. [state.md](state.md#что-задание-оставляет-в-рабочем-каталоге). |
| `CUDA_VISIBLE_DEVICES` | Для `submit --devices`: индексы в `--devices` считаются по GPU, видимым в текущем окружении, в их порядке. На `--gpus` не влияет. |

Окружение, в котором вы запускаете `cy-queue worker`, наследуют процессы заданий этого worker. Окружение команды `submit` в задание не попадает: задание получает окружение worker.

Переменные, которые очередь сама задаёт процессу задания:

| Переменная | Значение |
| --- | --- |
| `CUDA_VISIBLE_DEVICES` | UUID GPU из [выделенных GPU (allocation)](../GLOSSARY.md#allocation) через запятую, в порядке выделения. Задание видит только их. |
| `CY_HOME` | Рабочий каталог, записанный при `submit`. |
| `PYTHONUNBUFFERED` | `1`: вывод задания попадает в журнал без буферизации. |
| `CY_PROGRESS_FILE` | Путь `.cy/queue-status/<job-id>.json` в [рабочем каталоге (project)](../GLOSSARY.md#project), см. [state.md](state.md#что-задание-оставляет-в-рабочем-каталоге). |

Задать эти переменные, а также `CY_MODEL_PROCESS_OWNER` и `CY_DIRECT_MODEL_PROCESS_OWNER`, через Hydra (`hydra.job.env_set`) нельзя: `submit` отказывает с сообщением «Hydra environment overrides conflict with queue allocation ownership».

## Ошибки конфигурации

Все сообщения печатаются в stderr с префиксом `cy-queue:`, код завершения 1.

| Сообщение | Причина | Что делать |
| --- | --- | --- |
| `Queue configuration is missing: <path>. Create and fill [queue] with name, root and coordination_root before using the queue; set CY_QUEUE_CONFIG to use a different configuration file` | Файла по выбранному пути нет. | Создайте файл по этому пути или укажите другой в `CY_QUEUE_CONFIG`. |
| `Invalid queue configuration: expected [queue] with name, root and coordination_root; optional max_used_memory_gib must be a positive finite number` | Файл не разбирается как TOML, нет раздела `[queue]` или обязательного ключа, есть лишний ключ, неверный тип, пустое или непечатаемое `name`, недопустимое `max_used_memory_gib`. | Сверьте файл с [таблицей ключей](#раздел-queue). |
| `CY_QUEUE_CONFIG must be an absolute path` | В `CY_QUEUE_CONFIG` относительный путь. | Укажите абсолютный путь. |
| `HOME must be an absolute path` | `HOME` задана относительным путём, а `CY_QUEUE_CONFIG` и абсолютная `XDG_CONFIG_HOME` не заданы. | Исправьте `HOME` или задайте `CY_QUEUE_CONFIG`. |
| `queue.root must be an absolute path` | `root` в файле относительный. | Укажите абсолютный путь. |
| `queue.coordination_root must be an absolute path` | `coordination_root` в файле относительный. | Укажите абсолютный путь. |
| `--root must be an absolute path` | Флаг `--root` получил относительный путь. | Укажите абсолютный путь. |
| `CY_QUEUE_ROOT must be an absolute path` | Устаревшая `CY_QUEUE_ROOT` задана относительным путём. | Уберите переменную. |
| `CY_QUEUE_ROOT conflicts with the selected queue root; remove the legacy variable and configure CY_QUEUE_CONFIG or --root` | `CY_QUEUE_ROOT` указывает не на выбранный каталог очереди. | Уберите переменную. |
| `Queue configuration paths must name directories` | `root` (или `--root`) либо `coordination_root` указывает на существующий файл, а не на каталог. | Укажите каталог. |
| `Cannot determine the queue coordination filesystem` | Не удалось разобрать `/proc/self/mountinfo`, чтобы определить файловую систему `coordination_root`. | Проверьте, что `/proc` смонтирован и доступен процессу. |
| `Queue coordination_root requires a supported host-local Linux filesystem or NFS with hard,local_lock=flock and shared cache` | `coordination_root` лежит на неподдерживаемой файловой системе. | Выберите каталог по [требованиям](setup.md#каталог-координации). |
| `NFS coordination requires effective hard and local_lock=flock or local_lock=all with shared cache (no soft, softerr or nosharecache); check the mount options with your administrator` | `coordination_root` на NFS с неподходящими параметрами монтирования. | См. [требования к NFS](setup.md#каталог-координации). |
| `Host coordination is already bound to another location; stop workers and use the documented maintenance procedure` | На этом хосте уже используется другой `coordination_root`. Проверка выполняется любой подкомандой, кроме `config`. | Укажите тот же `coordination_root`, что у остальных пользователей хоста, см. [setup.md](setup.md#привязка-хоста-к-каталогу-координации). |

## См. также

- [setup.md](setup.md) — подготовка хоста и выбор каталогов.
- [state.md](state.md) — что лежит в каталогах очереди.
- [commands/config.md](commands/config.md) — команда `config`.
