# Формат вывода `--json`

С флагом `--json` команда `cy-queue` печатает вместо текста одну строку JSON. Эта страница описывает, какую запись печатает каждая подкоманда, её поля, их типы и смысл. Она нужна, когда вы разбираете вывод `cy-queue` скриптом, например берёте `revision` для `move --revision`.

## Что печатает каждая подкоманда

| Подкоманда | Что печатается |
| --- | --- |
| `config --json` | один объект [конфигурации](#конфигурация) |
| `submit --json` | список [записей задания](#запись-задания), по одной на каждое поставленное задание (у sweep их несколько) |
| `list --json` | один объект [вида очереди](#вид-очереди) |
| `move --json` | один объект [вида очереди](#вид-очереди) после перестановки |
| `cancel --json` | одна [запись задания](#запись-задания) после отмены |
| `recover --json` | одна [запись задания](#запись-задания) после восстановления |
| `archive --json` | один объект [вида очереди](#вид-очереди) после изменения; строка `Archived N job(s)` не печатается |
| `restore --json` | один объект [вида очереди](#вид-очереди) после изменения; строка `Restored N job(s)` не печатается |
| `gpu list --json` | список [записей GPU](#запись-gpu), по одной на каждый GPU |
| `gpu disable --json` | одна [запись удержания](#запись-удержания) |
| `gpu enable --json` | объект `{"status": "hold removed"}` |
| `gpu free --json`, `gpu release --json` | одна [запись освобождения GPU](#запись-освобождения-gpu) |

`worker` и `tui` флага `--json` не имеют.

## stdout, stderr и ошибки

- JSON печатается на stdout одной строкой с переводом строки в конце. Ничего другого команда на stdout не печатает.
- Символы вне ASCII экранируются: разделитель в `display_name` печатается как `\u00b7`, кириллица в `label` — как `\uXXXX`. Любой разбор JSON возвращает исходный текст.
- Если команда завершилась ошибкой, JSON не печатается совсем: stdout остаётся пустым, на stderr выводится строка `cy-queue: <сообщение>`, код завершения `1`. Пример:

  ```text
  cy-queue: Stale queue revision; refresh before reordering
  ```

- Ошибка аргументов (неизвестный флаг, нет обязательного аргумента) печатает usage и сообщение на stderr, код завершения `2`.
- Ошибка, которую `cy-queue` не переводит в такую строку, выводится на stderr как Python traceback, stdout остаётся пустым, код завершения `1`. Так выводится, например, ошибка составления конфигурации CY в `submit`, когда override задаёт несуществующий ключ (`hydra.errors.ConfigCompositionException`).

Поэтому скрипту достаточно проверить код завершения: при `0` на stdout лежит ровно одна строка JSON.

## Что скрыто в выводе

Вывод `--json` не показывает полные GPU UUID и секреты:

- **GPU.** Вместо `GPU-<uuid>` печатается номер GPU на хосте строкой (`"0"`, `"1"`), а если номер неизвестен, [короткое имя GPU](../../GLOSSARY.md#gpu-label) вида `gpu-<word>-<word>-<word>-<word>`. Для заданий другого хоста (`list --host`) всегда печатается короткое имя. Это относится к полям `request.devices`, `devices`, `gpu` и `claim.devices`, а также к GPU UUID внутри текстовых полей.
- **Текстовые поля** `display_name`, `command`, `label`, `error`, `waiting_reason`, строковый `progress`, `reason` удержания и `message` в `refresh_issues`: значения ключей вроде `password`, `token`, `secret`, заголовки `Authorization` и URL с логином или секретом заменяются на `<redacted>`; 64-символьные шестнадцатеричные токены — на `<redacted>`; прочие непрозрачные идентификаторы — на `[reference]` (UUID), `[revision]` (40 шестнадцатеричных символов) или `[task]` (32 символа); URL `http`, `https` или `clearml` с таким идентификатором — на `[ClearML link]`; управляющие ANSI-последовательности удаляются.
- **`clearml_url`**: из ссылки убирается только то, что содержит логин или секрет (тогда вместо неё `<redacted>`); обычная ссылка на задачу ClearML печатается целиком.
- **Не скрываются**: `id`, `host_id`, `boot_id`, `owner_uid`, `actor_uid`, `claim.job_id` печатаются полностью.
- **`config --json`** печатает пути и имя очереди как есть, без замен; текстовый вывод `config` проводит значения через те же замены, что и текстовые поля.

## Конфигурация

`config --json` печатает один объект:

| Поле | Тип | Описание |
| --- | --- | --- |
| `name` | строка | имя очереди, ключ `name` |
| `root` | строка | [каталог очереди (queue root)](../../GLOSSARY.md#queue-root), абсолютный путь |
| `coordination_root` | строка | [каталог координации (coordination root)](../../GLOSSARY.md#coordination-root), абсолютный путь |
| `config_path` | строка | путь к прочитанному файлу конфигурации |
| `root_source` | строка | откуда взят каталог очереди |
| `max_used_memory_gib` | число | [порог занятой памяти](../../GLOSSARY.md#memory-admission-threshold) в GiB |

Ключи и значения `root_source` описаны в [конфигурации](../configuration.md).

```json
{"name": "my-queue", "root": "/srv/cy-queue", "coordination_root": "/var/lib/cy-queue", "config_path": "/home/user/.config/clearml-yolo/queue.toml", "root_source": "config", "max_used_memory_gib": 2.0}
```

## Запись задания

Запись одного [задания (job)](../../GLOSSARY.md#job). Её печатают `submit` (в списке), `cancel` и `recover`, и она же входит в `jobs` [вида очереди](#вид-очереди).

| Поле | Тип | Описание |
| --- | --- | --- |
| `protocol` | число | версия формата записей очереди, сейчас `1` |
| `id` | строка | полный ID задания; его тоже принимают команды как `JOB` |
| `reference` | строка | [ссылка на задание](../../GLOSSARY.md#job-reference) `job-<N>` |
| `display_name` | строка | `Job <N> · <имя>`, где имя — `label`, а если оно пустое, `command` |
| `owner_uid` | число | UID [владельца](../../GLOSSARY.md#owner) |
| `host_id` | строка | ID хоста, в [разделе хоста (host partition)](../../GLOSSARY.md#host-partition) которого лежит задание |
| `boot_id` | строка | ID загрузки хоста, в которую задание поставлено в очередь |
| `command` | строка | команда CY: `pipeline` или `train` |
| `label` | строка | [имя задания (label)](../../GLOSSARY.md#label) |
| `request` | объект | [запрос GPU](../../GLOSSARY.md#gpu-request): `gpus` — число GPU или `null`; `devices` — список GPU по порядку или `null`. Заполнено ровно одно из двух |
| `submitted_at` | число | время постановки в очередь, Unix time в секундах |
| `submission_sequence` | число | номер `<N>` из `job-<N>` |
| `updated_at` | число | время последней записи состояния задания, Unix time. Его ставят запуск, возврат в очередь, завершение, `cancel` (переход в `cancelled` или `cancelling`), перевод в `recovery_required` и `recover`; `0`, пока состояние задания не менялось. Причина ожидания и прогресс его не меняют |
| `state` | строка | [состояние](../commands/list.md): `pending`, `starting`, `running`, `cancelling`, `completed`, `failed`, `cancelled`, `recovery_required` |
| `revision` | число | счётчик изменений этой записи задания (не путать с `revision` вида очереди) |
| `devices` | список строк | [выделенные GPU (allocation)](../../GLOSSARY.md#allocation); пустой, пока задание их не держит |
| `error` | строка или `null` | сообщение об ошибке задания. У задания, которое отменили после запуска его процесса, здесь `Job was cancelled` (см. [Отмену](../commands/worker.md#отмена)) |
| `waiting_reason` | строка или `null` | [причина ожидания (waiting reason)](../../GLOSSARY.md#waiting-reason) задания `pending`; у задания в другом состоянии `null`. Откуда берётся причина, см. ниже |
| `progress` | строка, число или `null` | прогресс, который сообщает запущенное задание |
| `clearml_url` | строка или `null` | ссылка на задачу ClearML |

```json
{"protocol": 1, "id": "<job-id>", "reference": "job-17", "display_name": "Job 17 \u00b7 my-run", "owner_uid": 1000, "host_id": "<host-id>", "boot_id": "<boot-id>", "command": "pipeline", "label": "my-run", "request": {"gpus": 1, "devices": null}, "submitted_at": 1795257549.27, "submission_sequence": 17, "updated_at": 0, "state": "pending", "revision": 0, "devices": [], "error": null, "waiting_reason": null, "progress": null, "clearml_url": null}
```

## Вид очереди

Его печатают `list`, `move`, `archive` и `restore`.

| Поле | Тип | Описание |
| --- | --- | --- |
| `protocol` | число | версия формата, сейчас `1` |
| `host_id` | строка | ID хоста, чей раздел показан |
| `revision` | число | [ревизия очереди](../../GLOSSARY.md#revision); её передают в `move --revision` |
| `jobs` | список | [записи заданий](#запись-задания) в порядке очереди, у каждой добавлено поле `archived` (логическое): задание в архиве |
| `archived_count` | число | сколько заданий раздела в архиве |
| `warning_count` | число | сколько элементов в `refresh_issues` |
| `refresh_issues` | список | задания из `jobs`, чьё текущее состояние сейчас не удалось прочитать: `job_id` (полный ID), `reference` (`job-<N>`), `message` (текст, по умолчанию `Status unavailable; showing last recorded state`) |

Какие задания попадают в `jobs`: `list` показывает вид, выбранный флагами `--archived` и `--all` (см. [list](../commands/list.md)); `move`, `archive` и `restore` всегда показывают обычный вид, без заданий в архиве. `waiting_reason`: `list`, `move`, `archive` и `restore` для своего хоста вычисляют текущую причину каждого задания `pending`, а `devices` заданий `starting`, `running`, `cancelling` и `recovery_required` берут из резервов в каталоге координации. `list --host` для другого хоста, а также `list` для задания с предупреждением обновления печатают причину, которую последней записал worker владельца, или `null`, если worker её ещё не записывал. У задания не в `pending` поле всегда `null`.

```json
{"protocol": 1, "host_id": "<host-id>", "revision": 2, "jobs": [{"protocol": 1, "id": "<job-id>", "reference": "job-17", "state": "pending", "waiting_reason": "Owner worker unavailable", "archived": false}], "archived_count": 0, "warning_count": 0, "refresh_issues": []}
```

(Запись задания внутри `jobs` сокращена.)

## Запись GPU

`gpu list --json` печатает список: по одной записи на каждый GPU, который видит NVML, и на каждый GPU, который очередь знает по своим записям, но NVML сейчас не видит (у такого `physical_index` равен `null`, а `gpu` — короткое имя).

| Поле | Тип | Описание |
| --- | --- | --- |
| `gpu` | строка | номер GPU на хосте строкой или короткое имя GPU |
| `physical_index` | число или `null` | номер GPU на хосте, `null`, если он неизвестен |
| `holds` | список | [записи удержания](#запись-удержания) на этом GPU, всех пользователей |
| `claim` | объект или `null` | задание, которое держит GPU в [резерве (reservation)](../../GLOSSARY.md#reservation): `job_id` (полный ID задания), `owner_uid`, `devices` (все GPU этого задания) |

```json
[{"gpu": "0", "physical_index": 0, "holds": [], "claim": {"job_id": "<job-id>", "owner_uid": 1000, "devices": ["0", "1"]}}, {"gpu": "2", "physical_index": 2, "holds": [], "claim": null}]
```

## Запись удержания

`gpu disable --json` печатает одну запись [удержания (hold)](../../GLOSSARY.md#hold), а `gpu list --json` — такие же записи в `holds`.

| Поле | Тип | Описание |
| --- | --- | --- |
| `gpu` | строка | номер GPU строкой или короткое имя GPU; в выводе `gpu disable` это номер, если селектор был номером, иначе короткое имя |
| `owner_uid` | число | UID пользователя, который поставил удержание |
| `host_id` | строка | ID хоста |
| `reason` | строка | причина, сейчас всегда `Operator disabled GPU` |
| `created_at` | число | время постановки удержания, Unix time |

Повторный `gpu disable` того же GPU тем же пользователем тоже завершается успешно и печатает запись с новым `created_at`.

```json
{"gpu": "0", "owner_uid": 1000, "host_id": "<host-id>", "reason": "Operator disabled GPU", "created_at": 1795257560.97}
```

## Ответ `gpu enable`

`gpu enable --json` печатает `{"status": "hold removed"}`, в том числе когда вашего удержания на этом GPU не было.

## Запись освобождения GPU

`gpu free --json` и `gpu release --json` печатают одну запись.

| Поле | Тип | Описание |
| --- | --- | --- |
| `gpu` | строка | номер GPU строкой, если селектор был номером, иначе короткое имя GPU |
| `actor_uid` | число | UID пользователя, который освободил GPU |
| `generation` | число | новый [номер поколения (generation)](../../GLOSSARY.md#gpu-generation) этого GPU, не меньше `1`; растёт с каждым освобождением, а также при повторном использовании GPU заданиями |
| `created_at` | число | время освобождения, Unix time |

```json
{"gpu": "1", "actor_uid": 1000, "generation": 1, "created_at": 1795257562.03}
```

## См. также

- [list](../commands/list.md) — таблица состояний и текстовый вывод очереди.
- [jobs](../commands/jobs.md) — `move`, `cancel`, `recover`, `archive`, `restore`.
- [gpu](../commands/gpu.md) — селекторы GPU, удержания и освобождение.
- [config](../commands/config.md) — вывод `config`.
- [GLOSSARY](../../GLOSSARY.md) — термины очереди.
