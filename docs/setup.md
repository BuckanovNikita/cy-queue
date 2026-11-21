# Подготовка хоста

Эта страница для того, кто ставит [очередь (queue)](../GLOSSARY.md#queue) на GPU-хост: требования к хосту, установка `cy-queue` рядом с CY, файл `queue.toml`, выбор двух каталогов, [привязка хоста (host binding)](../GLOSSARY.md#host-binding) к каталогу координации, работа нескольких пользователей и обновление. Остальные страницы считают, что всё это уже сделано.

## Требования

| Что | Требование |
| --- | --- |
| ОС | Linux. Нужны `/etc/machine-id` и `/proc/sys/kernel/random/boot_id`: по ним очередь узнаёт хост и текущую загрузку. |
| Python | `>=3.12.13,<3.14`. Для `worker` сборка Python должна давать `os.pidfd_open`, `os.waitid`, `os.P_PIDFD`, `os.pipe2`, `os.register_at_fork` и `signal.pidfd_send_signal`, а ядро — поддерживать pidfd и subreaper; иначе worker не стартует, а задание не запускается, с сообщением «Process supervision unavailable in …». Проверка выполняется при старте worker и перед запуском каждого задания тем интерпретатором, которым задание поставлено в очередь. |
| CY | `clearml-yolo>=0.38`, в том же окружении Python. |
| GPU | GPU NVIDIA, видимые через NVML (пакет `nvidia-ml-py` ставится как зависимость). Очередь выдаёт только целые GPU; GPU с включённым MIG не поддерживаются («MIG-enabled … is unsupported by GPU availability waiting»). |
| Файловые системы | Каталог очереди — любая файловая система, в том числе NFS. Каталог координации — см. [ниже](#каталог-координации). |
| `/tmp` | Каталог `/tmp/clearml-yolo-queue` общий для всех пользователей хоста, см. [привязку хоста](#привязка-хоста-к-каталогу-координации). |

## Установка

Ни `cy-queue`, ни CY не публикуются в индексе пакетов. `cy-queue` ставится из исходников (репозиторий <https://github.com/BuckanovNikita/cy-queue>) в то же окружение Python, в котором установлен CY (<https://github.com/BuckanovNikita/clearml-yolo>). Пакет даёт одну консольную команду `cy-queue`.

1. Установите CY по его инструкции.
2. Получите исходники `cy-queue`:

   ```bash
   git clone https://github.com/BuckanovNikita/cy-queue.git /path/to/cy-queue
   ```

3. Установите пакет в окружение CY (замените `/path/to/clearml-yolo/.venv` на окружение CY):

   ```bash
   uv pip install --python /path/to/clearml-yolo/.venv/bin/python -e /path/to/cy-queue
   ```

4. Проверьте, что команда доступна:

   ```bash
   /path/to/clearml-yolo/.venv/bin/cy-queue --help
   ```

Задание запоминает интерпретатор Python, которым его поставили в очередь, и запускается этим же интерпретатором, а не интерпретатором worker. Поэтому окружение, из которого выполняют `submit`, должно оставаться на месте и не меняться, пока задание не выполнено (см. [обновление](#обновление)).

## Файл `queue.toml`

Каждый пользователь, который ставит задания или запускает worker, создаёт свой файл. По умолчанию это `~/.config/clearml-yolo/queue.toml`; порядок поиска и все ключи описаны в [configuration.md](configuration.md). Минимальный пример:

```toml
[queue]
name = "my-queue"
root = "/srv/cy-queue"
coordination_root = "/var/lib/cy-queue"
```

Пользователи одного хоста, которые делят GPU, указывают одинаковые `root` и `coordination_root`. Проверьте файл:

```bash
cy-queue config
```

## Каталог очереди

`root` — [каталог очереди (queue root)](../GLOSSARY.md#queue-root). В нём лежат задания (job), их порядок и пометки архива. Он может быть на NFS и общим для нескольких хостов: у каждого хоста там свой [раздел хоста (host partition)](../GLOSSARY.md#host-partition), а `list --host` читает чужой раздел.

Если каталога нет, первый вызов очереди создаёт его с режимом `1777`. Уже существующий каталог сохраняет свой режим. Что внутри, описано в [state.md](state.md#каталог-очереди).

## Каталог координации

`coordination_root` — [каталог координации (coordination root)](../GLOSSARY.md#coordination-root). В нём лежат резервы GPU и удержания этого хоста. Его файловая система проверяется при каждом запуске `cy-queue` (по самой длинной точке монтирования, содержащей путь, из `/proc/self/mountinfo`).

Поддерживаемые локальные файловые системы: `btrfs`, `ext2`, `ext3`, `ext4`, `f2fs`, `jfs`, `nilfs2`, `ntfs3`, `overlay`, `ramfs`, `reiserfs`, `rootfs`, `tmpfs`, `ubifs`, `xfs`, `zfs`. Для любой другой (например, `cifs` или `fuse`) запуск завершается ошибкой:

```text
cy-queue: Queue coordination_root requires a supported host-local Linux filesystem or NFS with hard,local_lock=flock and shared cache
```

NFS (`nfs`, `nfs4`) допустим, если действующие параметры монтирования (как их показывает ядро, а не как они записаны в `fstab`) содержат:

- `hard`;
- ровно один из `local_lock=flock` или `local_lock=all`;
- ни одного из `soft`, `softerr`, `nosharecache`.

Иначе:

```text
cy-queue: NFS coordination requires effective hard and local_lock=flock or local_lock=all with shared cache (no soft, softerr or nosharecache); check the mount options with your administrator
```

Что из каталога координации переживает перезагрузку, описано в [state.md](state.md#что-переживает-перезагрузку).

## Привязка хоста к каталогу координации

Все пользователи хоста должны пользоваться одним каталогом координации, иначе два задания могли бы получить один GPU. Поэтому первый вызов `cy-queue` (любой подкоманды, кроме `config` и `--help`) записывает выбранный `coordination_root` в общий файл `/tmp/clearml-yolo-queue/<host-id>/coordination-root.json`. С этого момента хост привязан к этому каталогу.

Вызов с другим `coordination_root` завершается ошибкой, у любого пользователя:

```text
cy-queue: Host coordination is already bound to another location; stop workers and use the documented maintenance procedure
```

Исправьте `coordination_root` в `queue.toml` на тот, к которому привязан хост; его путь записан в поле `root` этого файла:

```bash
cat /tmp/clearml-yolo-queue/*/coordination-root.json
```

Если в каталоге `/tmp/clearml-yolo-queue/<host-id>/` уже есть записи о GPU (резервы, удержания), а привязки ещё нет, первая привязка к каталогу координации вне `/tmp/clearml-yolo-queue` отказывает:

```text
cy-queue: Existing host coordination evidence requires maintenance before relocation; keep the current coordination root to preserve recovery
```

`cy-queue` не переносит привязку сам. Порядок смены каталога координации на работающем хосте здесь не описан.

## Несколько пользователей на одном хосте

Каждый пользователь Linux ставит в очередь свои задания и запускает свой worker:

```bash
cy-queue worker
```

Worker выполняет только задания своего пользователя. На хосте допускается один живой worker на пользователя и каталог очереди; второй завершается ошибкой «One live queue worker per owner/root is already registered». Задание пользователя без живого worker ждёт с причиной `Owner worker unavailable`. Подробности — в [commands/worker.md](commands/worker.md).

Какие права нужны. Очередь сама создаёт каталоги с такими режимами (уже существующий каталог свой режим сохраняет):

| Путь | Режим | Кто пишет |
| --- | --- | --- |
| `/tmp/clearml-yolo-queue` и `/tmp/clearml-yolo-queue/<host-id>/` | `1777` | все пользователи хоста |
| `<coordination_root>` (если его нет) и `<coordination_root>/<host-id>/` | `1777` | все пользователи хоста |
| `<root>` (если его нет) | `1777` | первый пользователь создаёт в нём `hosts/` |
| `<root>/hosts/`, `<root>/hosts/<host-id>/`, `<root>/hosts/<host-id>/actors/` | `0777` | каждый пользователь создаёт свой каталог |
| `<root>/hosts/<host-id>/actors/<uid>/` и всё внутри | `0755`, файлы `0644` или `0600` | только владелец |

Если вы создаёте `root` или `coordination_root` заранее, дайте всем пользователям очереди право создавать в них каталоги и файлы. Каталог `<root>/hosts/<host-id>/actors/<uid>/` должен принадлежать своему пользователю и не быть доступным на запись другим, иначе чтение очереди отказывает с сообщением «Queue filesystem ownership mismatch» или «Owner-authored queue record is writable by another user».

Что пользователь видит и может сделать с чужими заданиями и удержаниями:

| Действие | Свои | Чужие |
| --- | --- | --- |
| Видеть задание в `list` и `tui`: имя, состояние, запрос GPU, выделенные GPU, причину ожидания, ошибку, прогресс, ссылку ClearML | да | да |
| Читать полную конфигурацию задания (снимок) | да | нет: файл `snapshot.json` доступен только владельцу |
| Читать журнал задания в `.cy/queue-logs/` | да | нет: каталог `0700`, файл `0600` |
| Переставить ожидающее задание (`move`) | да | да |
| `cancel`, `recover`, `archive`, `restore` | да | нет: «Only the effective job owner may change or execute this job» |
| Видеть удержания GPU (`gpu list`) с UID владельца | да | да |
| Снять удержание (`gpu enable`) | да | нет: снимается только своё |
| `gpu free` / `gpu release`: сбросить резерв и все удержания одного GPU | да | да, это действие любого пользователя |

Правила для `move`, `gpu free` и остальных команд описаны в [commands/jobs.md](commands/jobs.md) и [commands/gpu.md](commands/gpu.md).

## Обновление

При `submit` задание запоминает:

- абсолютный путь интерпретатора Python;
- версию установленного CY;
- [отпечаток окружения (package identity)](../GLOSSARY.md#package-identity): версию Python, имена и версии всех установленных пакетов и содержимое файлов пакетов `clearml_yolo` и `cy_queue`.

Перед запуском задания процесс задания сравнивает их с текущими и при расхождении не выполняет его:

| Сообщение | Что изменилось |
| --- | --- |
| `Queued package version changed; resubmit with the current installation` | версия CY |
| `Queued package identity changed; resubmit with the current installation` | любой установленный пакет, версия Python или файлы CY и `cy-queue` (в том числе правки в editable-установке) |
| `Queued interpreter changed; run the worker in the submitting environment` | процесс задания запущен не тем интерпретатором, который записан при `submit` |
| `Queued project or working directory is no longer available` | [рабочий каталог (project)](../GLOSSARY.md#project) или [текущий каталог (working directory)](../GLOSSARY.md#working-directory) `submit` удалён |

Поэтому после обновления CY, `cy-queue` или любого пакета окружения ожидающие задания, поставленные до обновления, не выполнятся. Отмените их (`cy-queue cancel job-17`) и поставьте в очередь заново из обновлённого окружения.

## См. также

- [configuration.md](configuration.md) — ключи `queue.toml` и переменные окружения.
- [state.md](state.md) — что очередь хранит на диске.
- [commands/worker.md](commands/worker.md) — запуск и остановка worker.
- [scenarios.md](scenarios.md) — первый запуск.
