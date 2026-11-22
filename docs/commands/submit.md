# cy-queue submit

`cy-queue submit` ставит в очередь (submit) одну команду CY или Hydra sweep. Команда собирает полную конфигурацию CY, замораживает её в [снимок задания (snapshot)](../../GLOSSARY.md#snapshot) и записывает по одному заданию (job) в состоянии `pending` на каждую конфигурацию. Сама команда ничего не запускает: задание выполняет worker владельца.

## Примеры

Поставить в очередь пайплайн CY на одну GPU:

```bash
cy-queue submit --gpus 1 -- ground_truth=data/ground_truth.csv
```

Поставить обучение на две GPU под своим именем задания:

```bash
cy-queue submit --command train --gpus 2 --label my-run -- ground_truth=data/ground_truth.csv
```

Поставить sweep: два задания, по одному на каждое значение `ultralytics.epochs`:

```bash
cy-queue submit --gpus 1 -- -m ground_truth=data/ground_truth.csv ultralytics.epochs=10,20
```

## Синтаксис и аргументы

```text
cy-queue [--root ROOT] submit [-h] [--command {pipeline,train}] (--gpus GPUS | --devices DEVICES) [--label LABEL] [--json] [--] [OVERRIDE ...]
```

| Аргумент | По умолчанию | Описание |
| --- | --- | --- |
| `--command {pipeline,train}` | `pipeline` | Какую команду CY поставить: `pipeline` — пайплайн, как у `cy`; `train` — обучение, как у `cy-train`. От этого зависит и имя конфигурации Hydra по умолчанию (`pipeline` или `train`). |
| `--gpus GPUS` | — | Сколько целых GPU нужно заданию; целое число больше нуля и не больше числа GPU на хосте. Worker выберет любые свободные GPU. |
| `--devices DEVICES` | — | Точные GPU по порядку: индексы CUDA через запятую, например `0,2`. Нужен ровно один из `--gpus` и `--devices`. |
| `--label LABEL` | имя задачи ClearML из конфигурации | [Имя задания (label)](../../GLOSSARY.md#label), которое печатают `submit` и `list`. Пустое или из одних пробелов не принимается. |
| `--json` | выключен | Печатать записи заданий в JSON вместо строк `Submitted ...`. |
| `OVERRIDE ...` | — | Override конфигурации CY в виде `key=value`, а также `-m`/`--multirun`, `--config-dir` (или `--config-path`) и `--config-name`. Необязательный разделитель `--` перед ними отбрасывается. |
| `-h`, `--help` | — | Показать справку и выйти. |

Глобальный флаг `--root` стоит перед `submit` и описан в [`config`](config.md).

### Где стоят флаги

Все флаги `submit` (`--command`, `--gpus`, `--devices`, `--label`, `--json`) пишутся до override. Всё, что начинается с первого override или с `--`, уходит в конфигурацию CY. Флаг `submit` после override отклоняется:

```text
$ cy-queue submit --gpus 1 ground_truth=data/ground_truth.csv --label x
cy-queue: After --, use Hydra overrides and optional -m/--config-dir/--config-name
```

`-m` и `--multirun` пишутся после `--` или после первого override. Сразу после флагов `submit` без `--` они не принимаются:

```text
$ cy-queue submit --gpus 1 -m ground_truth=data/ground_truth.csv
cy-queue: error: unrecognized arguments: -m
```

То же с `--json` после override: `cy-queue submit --gpus 1 -- ground_truth=data/ground_truth.csv --json` завершается ошибкой `After --, ...`; пишите `--json` до `--`.

Каждый override должен содержать `=`. Слово без `=` или другой флаг после `--` дают ту же ошибку `After --, ...`.

## Как это работает

1. Команда читает конфигурацию очереди (см. [конфигурацию](../configuration.md)).
2. Рабочий каталог — это `CY_HOME`, а если переменная не задана, текущий каталог.
3. Запрос GPU (GPU request) (см. [запрос GPU](../../GLOSSARY.md#gpu-request)):
   - `--gpus N` записывается как число. При постановке `N` сравнивается с числом GPU на хосте, которое сообщает NVML; `CUDA_VISIBLE_DEVICES` на это число не влияет. Если `N` больше, задание не ставится. Если NVML не отвечает, задание ставится без этой проверки, а на stderr печатается одно предупреждение `--gpus N was not checked against the host GPU count, which is unavailable: ...`;
   - `--devices` переводит индексы в UUID GPU сразу при постановке. Индекс считается по GPU, видимым в текущем окружении (`CUDA_VISIBLE_DEVICES` и порядок CUDA): `0` — первая видимая GPU. В задание попадают UUID, поэтому позднее изменение `CUDA_VISIBLE_DEVICES` его не меняет.
4. Hydra собирает конфигурацию CY: имя из `--config-name` (по умолчанию `pipeline` или `train`), каталог из `--config-dir` и override. Конфигурации CY описаны в [репозитории CY](https://github.com/BuckanovNikita/clearml-yolo).
5. Если указан `-m`/`--multirun` или в переопределениях либо в сохранённой конфигурации стоит `hydra.mode=MULTIRUN`, Hydra разворачивает sweep: одно задание на каждую комбинацию значений. Все задания sweep получают один и тот же запрос GPU, свой каталог вывода Hydra и один общий новый тег ClearML, который добавляется к `clearml.tags` (заданные вами теги сохраняются). Каждая постановка sweep создаёт новый тег; задание, поставленное не как sweep, тега не получает. Значения через запятую без `-m` и без `hydra.mode=MULTIRUN` не разворачиваются: команда завершается с ошибкой `Use -m or hydra.mode=MULTIRUN to expand a Hydra sweep`.
6. Каждая конфигурация проверяется: override устройств, переменные окружения Hydra, пути записи и настройки команды (см. [Частые ошибки](#частые-ошибки)). Если хотя бы одна конфигурация sweep не проходит проверку, в очередь не попадает ни одно задание.
7. Для каждой конфигурации замораживается снимок: полная конфигурация, команда, имя задания, [рабочий каталог (project)](../../GLOSSARY.md#project), [текущий каталог (working directory)](../../GLOSSARY.md#working-directory), путь к интерпретатору Python, версия CY и [отпечаток окружения (package identity)](../../GLOSSARY.md#package-identity): версия Python, имена и версии всех установленных пакетов и файлы установленного кода CY и cy-queue. Позднее изменение файлов конфигурации на задание не влияет.
8. Задания записываются в [раздел хоста (host partition)](../../GLOSSARY.md#host-partition) каталога очереди в состоянии `pending`, в конец очереди. Задание получает следующий номер в разделе хоста: на единицу больше самого большого номера в нём. Номер не меняется при `move`, архиве и перезапуске worker и не достаётся другому заданию.

Что проверяется позже, когда worker запускает задание: версия CY и отпечаток окружения не изменились, интерпретатор тот же, рабочий и текущий каталоги существуют. Проверку выполняет сам процесс задания, когда задание уже `running` и занимает свои GPU. При расхождении процесс сразу завершается, и задание становится `failed` с ошибкой `Native process exited with status 1`. Причина записана в журнале задания: `Queued package version changed; resubmit with the current installation`, `Queued package identity changed; resubmit with the current installation`, `Queued interpreter changed; run the worker in the submitting environment` или `Queued project or working directory is no longer available`. Такое задание нужно поставить заново. Поэтому после установки или обновления любого пакета в окружении поставьте ожидающие задания заново.

При запуске очередь сама задаёт устройства всех фаз CY по выделенным GPU (allocation); фазы, где явно указан `cpu`, остаются на CPU.

## Результат

Без `--json` команда печатает строку на каждое задание:

```text
Submitted Job 17 · my-run
```

`17` — номер задания. [Ссылка на задание (job reference)](../../GLOSSARY.md#job-reference) для других команд — `job-17`. Имя задания — `--label`, иначе `clearml.task_name` из конфигурации CY, иначе `Pipeline` или `Train`.

С `--json` команда печатает один JSON-массив записей заданий; поле `reference` содержит `job-17`. Поля описаны в [формате JSON](../formats/json.md).

Пока worker владельца не запущен, задание ждёт в `pending` с причиной ожидания `Owner worker unavailable`:

```text
1	Job 17 · my-run	uid=1000	pending	request=1	allocation=-	Owner worker unavailable
```

Запустите [`cy-queue worker`](worker.md) от того же пользователя.

### Коды завершения

| Код | Когда |
| --- | --- |
| `0` | Задания записаны. |
| `1` | Ошибка конфигурации очереди, запроса GPU, конфигурации CY или записи; обычно сообщение начинается с `cy-queue:`. |
| `2` | Ошибка аргументов: нет `--gpus`/`--devices`, оба сразу, неизвестный флаг. |

## Частые ошибки

`one of the arguments --gpus --devices is required` — не указан запрос GPU. Добавьте `--gpus N` или `--devices`.

`argument --devices: not allowed with argument --gpus` — указаны оба. Оставьте один.

`--devices must contain comma-separated nonnegative CUDA indexes` — в `--devices` не число. `--devices must contain unique nonnegative CUDA indexes` — отрицательный или повторённый индекс.

`--devices selects a GPU outside the inherited CUDA visibility` — индекс не меньше числа видимых GPU (индексы считаются с `0`). Проверьте `CUDA_VISIBLE_DEVICES` в этой оболочке.

`Use -m or hydra.mode=MULTIRUN to expand a Hydra sweep` — в переопределении несколько значений через запятую, а sweep не запрошен. Добавьте `-m` после `--`.

`--gpus must be a positive integer` — `--gpus 0` или отрицательное число.

`--gpus N exceeds the M GPU(s) on this host` — `--gpus` просит больше GPU, чем есть на хосте: такое задание никогда бы не запустилось. Уменьшите `N` до `M` или меньше.

`Job label must be nonempty` — пустой `--label`.

`After --, use Hydra overrides and optional -m/--config-dir/--config-name` — после override стоит флаг `submit` или слово без `=`. Перенесите флаги `submit` до override.

`ultralytics.device conflicts with the queue allocation; use cy-queue --devices or --gpus, and remove native GPU device overrides (explicit CPU phases are supported)` — устройство GPU задано override или в своей конфигурации CY. Значения `cuda` и `-1`, которые пришли из конфигурации по умолчанию, а не из override, допускаются: очередь заменит их при запуске. Так проверяются ключи `ultralytics.device`, `ultralytics_predict.device`, `model.train.device`, `model.predict.device`, `comparison.device` и `export.device`; в сообщении стоит ключ, который нарушил правило. Значение `cpu` разрешено. Уберите override и выберите GPU через `--gpus` или `--devices`.

`Hydra environment overrides conflict with queue allocation ownership` — в `hydra.job.env_set` задана переменная, которой управляет очередь: `CUDA_VISIBLE_DEVICES`, `CY_HOME`, `CY_MODEL_PROCESS_OWNER`, `CY_DIRECT_MODEL_PROCESS_OWNER`, `CY_PROGRESS_FILE` или `PYTHONUNBUFFERED`. Другие переменные разрешены.

`Legacy queue/autogpu controls are removed; use cy-queue allocation options` — override ключей `queue.*`, `autogpu.*`, `auto_gpu.*` или `hydra/launcher`. Уберите его и используйте `--gpus` или `--devices`.

`Project write destination ... must be contained beneath CY_HOME=...` — путь записи (например, `run_dir`) выходит за рабочий каталог. Выберите путь внутри рабочего каталога.

`Cannot find primary config '...'` — нет конфигурации с именем из `--config-name`. Проверьте `--config-dir` и `--config-name`.

`Missing mandatory setting ground_truth; add the override ground_truth=<value>` — не задан обязательный ключ CY; в сообщении стоит его имя. Добавьте его override, например `ground_truth=data/ground_truth.csv`.

Сообщения о конфигурации очереди описаны в [конфигурации](../configuration.md).

## См. также

- [`cy-queue worker`](worker.md) — запуск заданий.
- [`cy-queue list`](list.md) — состояния и причины ожидания.
- [`cy-queue move`, `cancel`, `archive`](jobs.md) — управление заданиями.
- [Формат JSON](../formats/json.md).
- [Сценарии](../scenarios.md).
