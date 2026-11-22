# cy-queue worker

`cy-queue worker` запускает [worker](../../GLOSSARY.md#worker): процесс, который берёт из очереди ваши [задания](../../GLOSSARY.md#job) (job) и запускает их на GPU этого хоста. Worker обслуживает только задания своего пользователя и работает, пока его не остановят, поэтому каждый пользователь держит свой worker запущенным в отдельном терминале или как сервис.

## Примеры

```bash
cy-queue worker
```

Запускает worker с журналом уровня `INFO`: запуск, изменения ваших заданий и heartbeat раз в минуту.

```bash
cy-queue worker --log-level DEBUG
```

То же, но с записью о каждом опросе очереди.

```bash
cy-queue worker --log-level WARNING
```

Оставляет в журнале только ошибки ваших заданий (`failed`, `recovery_required`).

## Синтаксис и аргументы

```text
cy-queue [--root ROOT] worker [-h] [--log-level {DEBUG,INFO,WARNING,ERROR}]
```

| Аргумент | По умолчанию | Описание |
| --- | --- | --- |
| `--log-level {DEBUG,INFO,WARNING,ERROR}` | `INFO` | Подробность журнала worker в stderr; см. [Журнал](#журнал). |
| `-h`, `--help` | | Печатает справку и завершает работу. |

Глобальный флаг `--root` описан в [Конфигурации](../configuration.md#флаг---root).

## Как это работает

### Запуск и регистрация

1. Worker читает конфигурацию (`name`, `root`, `coordination_root`, `max_used_memory_gib`) один раз при запуске. Изменённый `queue.toml` подействует после перезапуска worker.
2. Worker проверяет, что Python на этом хосте поддерживает надзор за процессами Linux. Если нет, он завершается с ошибкой.
3. Worker регистрируется: на хосте может работать только один worker одного пользователя для одного [каталога очереди](../../GLOSSARY.md#queue-root) (queue root). Второй worker того же пользователя сразу завершается с кодом `1` и сообщением `One live queue worker per owner/root is already registered`; строку `Starting queue worker` он не печатает. Worker другого пользователя не мешает вашему.
4. Раз в секунду worker опрашивает очередь и отмечает, что он жив. Ваши задания в `list` считаются обслуживаемыми, пока последняя отметка не старше 10 секунд и процесс worker существует. Иначе у ожидающих заданий причина ожидания `Owner worker unavailable`.

### Выбор следующего задания

На каждом опросе, если в очереди есть задания `pending`:

1. Worker читает занятую память видимых ему GPU (видимость задаёт `CUDA_VISIBLE_DEVICES` окружения worker). GPU считается свободной, только если её занятая память строго меньше [`max_used_memory_gib`](../configuration.md#раздел-queue). GPU, память которой прочитать не удалось, считается занятой; остальные GPU при этом остаются доступны. Если драйвер не отвечает совсем или набор видимых GPU изменился с запуска worker, в этот опрос worker не запускает ничего, а его ожидающие задания получают [причину ожидания](../../GLOSSARY.md#waiting-reason) (waiting reason) `GPU memory telemetry unavailable`.
2. Из свободных GPU исключаются GPU с [резервом](../../GLOSSARY.md#reservation) (reservation) любого задания и GPU, на которых стоит [удержание](../../GLOSSARY.md#hold) (hold) любого пользователя (`gpu disable`). Резервы и удержания общие для всех очередей хоста с тем же каталогом координации.
3. Worker проходит очередь сверху вниз в её порядке (`list`, `move`) и выбирает первое задание `pending`, у владельца которого есть живой worker и весь запрос которого помещается в свободные GPU этого владельца:
   - запрос `--gpus N` берёт первые `N` свободных GPU в порядке видимости CUDA у worker владельца;
   - запрос `--devices` подходит, только если свободны все названные GPU; тогда задание получает ровно их и в том же порядке.
   Задания, которые не помещаются, пропускаются, и следующее задание может запуститься раньше них. Задания пользователей без живого worker тоже пропускаются.
4. Если выбранное задание чужое, ваш worker в этот опрос ничего не запускает: задание запустит worker его владельца. Ваше задание ниже по очереди ждёт с причиной `Waiting for an earlier runnable job`.
5. Если выбранное задание ваше, worker его запускает.

Причины ожидания перечислены на странице [list](list.md#причины-ожидания).

### Запуск задания

1. Worker проверяет, что интерпретатор Python из [снимка задания](../../GLOSSARY.md#snapshot) (snapshot) существует и поддерживает надзор за процессами. Если проверка не прошла, worker завершается с кодом `1` (`cy-queue: Cannot probe process supervision in <интерпретатор>: ...` или `cy-queue: Process supervision ...`), а задание остаётся `pending`. Иначе задание переходит в `starting`.
2. Worker запускает для задания отдельный процесс [guardian](../../GLOSSARY.md#guardian) в собственной сессии, отвязанный от терминала worker. Guardian занимает выбранные GPU и держит их резерв.
3. Перед самым стартом guardian ещё раз читает память выделенных GPU. Если какая-то из них недоступна или занята не меньше порога, задание возвращается в `pending` с причиной `GPU memory is unavailable or at least <порог> GiB at startup`. Если резерв GPU успели снять (`gpu free`), причина будет `GPU allocation was freed before startup`. Если за это время задание отменили, оно становится `cancelled`.
4. Задание переходит в `running`, и guardian запускает процесс задания.
5. Процесс задания сверяет снимок с текущей установкой и завершается с ошибкой (задание станет `failed`, сообщение будет в журнале задания), если изменились версия или установка CY (`Queued package version changed; resubmit with the current installation`, `Queued package identity changed; resubmit with the current installation`), интерпретатор (`Queued interpreter changed; the recorded interpreter started a different Python executable (a launcher or an alias); resubmit by running cy-queue submit with the real Python interpreter, not through a launcher or an alias`) или пропал [рабочий каталог (project)](../../GLOSSARY.md#project) (`Queued project or working directory is no longer available`).
6. Затем процесс переходит в [текущий каталог (working directory)](../../GLOSSARY.md#working-directory), который был текущим при `submit`, и запускает команду CY (`pipeline` или `train`) интерпретатором из снимка, с замороженной конфигурацией, в которой устройства привязаны к выделенным GPU: обучение получает все выделенные GPU, предсказание, сравнение и экспорт — первую из них. Фазы, где явно указан `cpu`, остаются на CPU.

Если guardian не перевёл задание из `starting` за 10 секунд или его процесс исчез сразу после запуска, задание становится `recovery_required`.

### Что получает процесс задания

Процесс задания наследует окружение процесса worker, а не окружение терминала, из которого выполнялся `submit`. Поверх него guardian и процесс запуска задают:

| Переменная окружения | Значение |
| --- | --- |
| `CUDA_VISIBLE_DEVICES` | UUID выделенных GPU через запятую, в порядке выделения (`GPU-<uuid>,GPU-<uuid>`). |
| `CY_HOME` | Рабочий каталог задания из снимка. |
| `PYTHONUNBUFFERED` | `1`. |
| `CY_PROGRESS_FILE` | Файл прогресса задания `.cy/queue-status/<job-id>.json` в рабочем каталоге. |

Кроме них процесс получает служебные переменные, через которые guardian следит за ним.

### Куда пишется вывод

stdout и stderr процесса задания дописываются в `.cy/queue-logs/<job-id>.log` в рабочем каталоге задания, где `<job-id>` — полный ID задания из `--json`. Worker в этот файл не пишет. Подробнее в [Состоянии на диске](../state.md#что-задание-оставляет-в-рабочем-каталоге).

### Конец задания

1. Когда процесс задания завершается, guardian завершает всех его потомков и проверяет, что их не осталось.
2. Задание получает состояние:
   - `completed`, если процесс вышел с кодом `0`;
   - `failed` с ошибкой `Native process exited with status <код>`, если код не `0`;
   - `failed` с ошибкой `Guardian operation failed: <тип ошибки>`, если сам guardian не смог довести задание до конца.
3. Только после этого guardian снимает резерв GPU, и они становятся доступны следующему заданию на ближайшем опросе любого worker.
4. Если проверить завершение потомков не удалось, задание становится `recovery_required` с ошибкой `Cleanup verification failed: <тип ошибки>; owner recovery required`. Guardian после этого завершается, и резерв GPU заканчивается вместе с ним (см. [ниже](#когда-задание-требует-восстановления)).

### Отмена

`cancel` для задания `starting` или `running` переводит его в `cancelling`. Guardian посылает процессу задания `SIGTERM` и ждёт до 90 секунд, чтобы команда CY успела завершиться сама. Затем guardian завершает всё дерево процессов, задание становится `cancelled`, и только тогда снимается резерв GPU. В поле `error` задания, отменённого после запуска его процесса, записано `Job was cancelled`; код завершения процесса не записывается. Задание, отменённое до запуска команды CY (в `pending`, при подготовке, при отложенном старте или при проверке guardian перед запуском, когда процесс задания уже создан, а команда CY ещё не запущена), остаётся без ошибки. Если сам guardian не смог довести задание до конца, ошибка — `Guardian operation failed: <тип ошибки>`. Одно исключение: если `cancel` приходит в короткий промежуток после этой проверки, но до того, как guardian переводит задание из `starting` в `running`, задание становится `cancelled` с ошибкой `Guardian operation failed: RuntimeError`, хотя guardian исправен. Отмена ожидающего задания описана в [jobs](jobs.md).

### Передача GPU между этапами пайплайна

Команда `pipeline`, получившая несколько GPU, после окончания обучения сообщает об этом guardian. Guardian оставляет заданию первую GPU из выделенных, снимает резерв с остальных, и `list` показывает в `allocation=` одну GPU. Освобождённые GPU сразу доступны другим заданиям, пока пайплайн продолжает работу на оставшейся. С одной GPU ничего не меняется.

### Остановка worker

Worker останавливается по `SIGINT` (Ctrl+C) или `SIGTERM`. Он заканчивает текущий опрос, снимает регистрацию, пишет `Queue worker stopped; active jobs remain supervised by their guardians` и выходит с кодом `0`.

Запущенные задания при этом продолжают работать: ими управляют их guardian, а не worker. То же происходит, если worker убит (`SIGKILL`) или упал. Пока ваш worker не работает:

- ваши ожидающие задания не запускаются и в `list` имеют причину `Owner worker unavailable`;
- задание, чей guardian пропал без проверенной очистки, будет переведено в `recovery_required` только при следующем запуске вашего worker.

Новый worker можно запустить сразу: регистрация остановленного или погибшего worker не мешает.

### Когда задание требует восстановления

Ваш worker на каждом опросе проверяет ваши задания и переводит задание в [`recovery_required`](../../GLOSSARY.md#recovery-required), когда:

| Ошибка задания | Причина |
| --- | --- |
| `Guardian exited without verified cleanup; owner recovery required` | Guardian задания больше не существует (например, убит или хост перезагружен), и никто не подтвердил, что процессы задания завершены. |
| `Execution state is uncertain; owner recovery required` | Задание в `starting`, `running` или `cancelling`, но ни guardian, ни процесса запуска нет. |
| `Guardian identity disappeared before startup` | Guardian исчез сразу после запуска. |
| `Guardian startup did not complete; owner recovery required` | Guardian не перевёл задание из `starting` за 10 секунд. |
| `Cleanup verification failed: <тип ошибки>; owner recovery required` | Guardian не смог подтвердить, что все процессы задания завершены. |

Резерв GPU держит guardian задания, пока работает. Когда guardian пропал, резерва уже нет: `gpu list` показывает GPU без задания, а `list` — `allocation=-`. Оставшиеся процессы задания при этом могут продолжать работать и занимать GPU, и другое задание получит этот GPU, если занятая память ниже [`max_used_memory_gib`](../configuration.md#раздел-queue). Остановите оставшиеся процессы командой [`recover`](jobs.md#recover).

### Журнал

Worker пишет журнал в stderr строками вида `ГГГГ-ММ-ДД ЧЧ:ММ:СС | УРОВЕНЬ | сообщение`; в stdout он ничего не печатает.

| Запись | Уровень | Когда |
| --- | --- | --- |
| `Starting queue worker \| queue=<name> root=<root> host=<host> uid=<uid> max_used_memory_gib=<порог>` | `INFO` | После регистрации worker, один раз; отказанный второй worker её не печатает. |
| `Job <N> · <имя> \| state=<state> \| request=<запрос> \| allocation=<GPU>` и, если есть, `\| waiting=<причина>`, `\| progress=<прогресс>`, `\| error=<ошибка>` | `INFO`; `ERROR` для `failed` и `recovery_required` | Когда у вашего задания меняется состояние, GPU, причина ожидания, прогресс или ошибка. Уже завершённые задания при запуске worker не повторяются. |
| `Worker heartbeat \| active \| <state>=<число> ...` или `Worker heartbeat \| idle \| no jobs` | `INFO` | При первом опросе и затем не чаще раза в 60 секунд. `active`, если у вас есть задания в `pending`, `starting`, `running`, `cancelling` или `recovery_required`. |
| `Worker poll \| host=<host> uid=<uid> \| <state>=<число> ...` | `DEBUG` | На каждом опросе. |
| `Queue worker stopped; active jobs remain supervised by their guardians` | `INFO` | После остановки сигналом. |

Уровень `--log-level` оставляет записи этого уровня и выше: `DEBUG` показывает всё, `INFO` всё, кроме опросов, `WARNING` и `ERROR` только строки заданий уровня `ERROR`. GPU в журнале названы физическими номерами или [короткими именами](../../GLOSSARY.md#gpu-label).

## Результат

Worker ничего не печатает в stdout. Его действия видны в журнале (stderr), в `cy-queue list` и в файлах задания в рабочем каталоге ([Состояние на диске](../state.md#что-задание-оставляет-в-рабочем-каталоге)).

### Коды завершения

| Код | Когда |
| --- | --- |
| `0` | Worker остановлен сигналом `SIGINT` или `SIGTERM`. |
| `1` | Ошибка: конфигурация, уже работающий worker того же пользователя, отсутствие надзора за процессами у Python worker или у интерпретатора задания, ошибка доступа к очереди во время работы. Сообщение печатается в stderr как `cy-queue: <ошибка>`, а запись `Queue worker stopped` не появляется. |
| `2` | Неверный аргумент командной строки. |

## Частые ошибки

| Сообщение | Причина и решение |
| --- | --- |
| `cy-queue: One live queue worker per owner/root is already registered` | Ваш worker для этого каталога очереди уже работает на хосте. Пользуйтесь им или остановите его перед запуском нового. |
| `cy-queue: Process supervision requires Linux: ...`, `cy-queue: Process supervision unavailable in ...` | Python не даёт нужных возможностей Linux (pidfd, subreaper, `/proc`). Запускайте worker на Linux с полноценной сборкой Python. |
| `cy-queue: Owner worker lock belongs to another UID` | Файл регистрации worker в каталоге координации принадлежит другому пользователю. См. [Состояние на диске](../state.md#каталог-координации). |
| `cy-queue: Cannot probe process supervision in <интерпретатор>: ...` | Интерпретатор, из которого выполнялся `submit`, больше не существует (например, окружение удалено). Worker останавливается на этом задании при каждом запуске. Отмените задание (`cancel`, см. [jobs](jobs.md)) и поставьте его в очередь заново из рабочего окружения. |
| Задание `failed`, в журнале задания `Queued package version changed; resubmit with the current installation` | CY обновили после `submit`. Поставьте задание в очередь заново. |
| Задания стоят с `Owner worker unavailable` | Ваш worker не запущен или не отвечает. Запустите `cy-queue worker`. |
| Задания стоят с `GPU memory telemetry unavailable` | Worker не смог прочитать память GPU (драйвер не ответил) или набор видимых ему GPU изменился с его запуска. Проверьте GPU и драйвер (`nvidia-smi`); если менялись GPU, перезапустите worker. |

## См. также

- [list и tui](list.md): состояния заданий и причины ожидания.
- [Управление заданиями](jobs.md): `cancel`, `recover`.
- [gpu](gpu.md): удержания и освобождение GPU.
- [Конфигурация](../configuration.md): `max_used_memory_gib` и другие ключи.
- [Состояние на диске](../state.md): журналы и файлы статуса заданий.
- [Сценарии](../scenarios.md).
