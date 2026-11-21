# Сценарии

Три цепочки команд от начала до конца: первый запуск, sweep с управлением очередью и восстановление после сбоя. Каждый шаг ссылается на страницу команды, где описаны подробности. [Очередь (queue)](../GLOSSARY.md#queue) на хосте уже настроена ([Подготовка хоста](setup.md)), команды выполняются из [рабочего каталога (project)](../GLOSSARY.md#project) `/workspace/project`.

## 1. Первый запуск

1. Проверьте конфигурацию ([`config`](commands/config.md)):

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

   Если вместо этого напечатано `cy-queue: Queue configuration is missing: ...`, создайте `queue.toml` ([Конфигурация](configuration.md)).

2. Поставьте в очередь (submit) одно [задание (job)](../GLOSSARY.md#job) на одну GPU ([`submit`](commands/submit.md)):

   ```bash
   cy-queue submit --gpus 1 --label my-run -- ground_truth=data/ground_truth.csv
   ```

   ```text
   Submitted Job 17 · my-run
   ```

   [Ссылка на задание (job reference)](../GLOSSARY.md#job-reference) для других команд — `job-17`.

3. Посмотрите очередь ([`list`](commands/list.md)):

   ```bash
   cy-queue list
   ```

   ```text
   my-queue | gpu-host | revision 1 | archived 0 | warnings 0
   1	Job 17 · my-run	uid=1000	pending	request=1	allocation=-	Owner worker unavailable
   ```

   Причина `Owner worker unavailable` значит, что ваш [worker](../GLOSSARY.md#worker) ещё не запущен: `submit` сам ничего не запускает.

4. В отдельном терминале запустите свой worker ([`worker`](commands/worker.md)) и оставьте его работать:

   ```bash
   cy-queue worker
   ```

   Worker запускает только ваши задания. Второй worker того же пользователя для того же каталога очереди завершается с `One live queue worker per owner/root is already registered`.

5. Снова посмотрите очередь. Когда GPU свободна, задание проходит `pending` → `starting` → `running` и заканчивается в `completed` или `failed`; что значит каждое состояние, описано в [таблице состояний](commands/list.md#состояния-заданий):

   ```bash
   cy-queue list
   ```

   ```text
   my-queue | gpu-host | revision 4 | archived 0 | warnings 0
   1	Job 17 · my-run	uid=1000	running	request=1	allocation=0	
   ```

   Номер ревизии в ваших выводах будет другим: он растёт при каждом изменении очереди.

6. Тот же вид с автообновлением открывает [`tui`](commands/list.md#cy-queue-tui); закрыть его — `q`, worker и задания при этом продолжают работать:

   ```bash
   cy-queue tui
   ```

7. Найдите журнал задания ([Состояние на диске](state.md#что-задание-оставляет-в-рабочем-каталоге)). Возьмите полный ID задания из поля `id`, затем откройте журнал:

   ```bash
   cy-queue list --json
   tail -f /workspace/project/.cy/queue-logs/<job-id>.log
   ```

   Журнал содержит stdout и stderr процесса задания. Для задания `failed` причина есть и в поле `error` вывода `--json`.

## 2. Sweep и управление очередью

В этом сценарии ваш worker остановлен (Ctrl+C в его терминале), поэтому новые задания ждут с причиной `Owner worker unavailable`, а ревизия очереди меняется только от ваших команд. При работающем worker первое подходящее задание запустится сразу, и ревизия будет расти сама.

1. Поставьте [sweep](../GLOSSARY.md#sweep): по одному заданию на каждое значение `ultralytics.epochs` ([`submit`](commands/submit.md)). `-m` стоит после `--`. Без `--label` имя задания — имя задачи ClearML из конфигурации CY:

   ```bash
   cy-queue submit --gpus 1 --label my-run -- -m ground_truth=data/ground_truth.csv ultralytics.epochs=10,20
   ```

   ```text
   Submitted Job 18 · my-run
   Submitted Job 19 · my-run
   ```

   Без `--` перед `-m` команда завершается с `cy-queue: error: unrecognized arguments: -m`.

2. Посмотрите очередь и [ревизию очереди (revision)](../GLOSSARY.md#revision) в первой строке ([`list`](commands/list.md)):

   ```bash
   cy-queue list
   ```

   ```text
   my-queue | gpu-host | revision 12 | archived 0 | warnings 0
   1	Job 17 · my-run	uid=1000	completed	request=1	allocation=0	
   2	Job 18 · my-run	uid=1000	pending	request=1	allocation=-	Owner worker unavailable
   3	Job 19 · my-run	uid=1000	pending	request=1	allocation=-	Owner worker unavailable
   ```

3. Поставьте `job-19` первым среди ожидающих, передав ревизию из `list` ([`move`](commands/jobs.md#move)):

   ```bash
   cy-queue move job-19 top --revision 12
   ```

   Команда печатает очередь с новой ревизией (`revision 13`). Следующий `move` берёт уже её:

   ```bash
   cy-queue move job-19 after job-18 --revision 13
   ```

   Если очередь успела измениться, команда ничего не меняет и печатает `Stale queue revision; refresh before reordering`: снова выполните `cy-queue list` и повторите с новой ревизией.

4. Отмените одно задание ([`cancel`](commands/jobs.md#cancel)):

   ```bash
   cy-queue cancel job-18
   ```

   ```text
   Job 18 · my-run: cancelled
   ```

5. Уберите завершённые задания в [архив](../GLOSSARY.md#archive) ([`archive`](commands/jobs.md#archive)). Архивировать можно только свои задания в `completed`, `failed` или `cancelled`:

   ```bash
   cy-queue archive job-18
   ```

   ```text
   Archived 1 job(s)
   ```

   Вслед за этой строкой команда печатает очередь без архивных заданий. Архивные задания показывает `cy-queue list --archived`, все вместе — `cy-queue list --all`.

6. Верните задание из архива ([`restore`](commands/jobs.md#restore)):

   ```bash
   cy-queue restore job-18
   ```

   ```text
   Restored 1 job(s)
   ```

7. Снова запустите worker (`cy-queue worker`), чтобы оставшееся задание выполнилось.

## 3. Восстановление после сбоя

1. В `list` задание стоит в состоянии `recovery_required` — [требуется восстановление (recovery required)](../GLOSSARY.md#recovery-required): очередь не знает, остались ли процессы задания. [Резерв (reservation)](../GLOSSARY.md#reservation) GPU держал guardian задания; если guardian пропал, резерва уже нет, а оставшиеся процессы могут продолжать занимать GPU. Причину показывает поле `error` в `cy-queue list --json`; возможные ошибки перечислены в [worker](commands/worker.md#когда-задание-требует-восстановления). В это состояние задание переводит worker владельца; если [guardian (процесс-надзиратель задания)](../GLOSSARY.md#guardian) пропал, пока ваш worker был остановлен, задание станет `recovery_required` при следующем запуске worker.

2. Посмотрите, что очередь знает о GPU ([`gpu list`](commands/gpu.md#gpu-list)), и проверьте через `nvidia-smi`, не занимают ли GPU оставшиеся процессы задания:

   ```bash
   cy-queue gpu list
   nvidia-smi
   ```

   ```text
   0	holds=-	job=-
   1	holds=-	job=-
   ```

   После гибели guardian `gpu list` показывает GPU задания без резерва (`job=-`), даже если его процессы ещё работают.

3. Восстановите задание ([`recover`](commands/jobs.md#recover)). Это может сделать только владелец:

   ```bash
   cy-queue recover job-17
   ```

   ```text
   Job 17 · my-run: cancelled
   ```

   `recover` останавливает оставшиеся процессы задания и снимает его резерв. Если guardian задания ещё жив, команда отказывает с `Guardian is still alive; cancel it before attempting recovery`: выполните `cy-queue cancel job-17` и дождитесь его завершения. При `GPU guardian still owns its locks; recovery refused` повторите позже. `cancel` сам по себе состояние `recovery_required` не меняет.

4. Если `gpu list` показывает GPU в резерве (`job=owned by user ...`) задания, которое уже не выполняется, освободите его ([`gpu free` или `gpu release`](commands/gpu.md#gpu-free-и-gpu-release) — одна команда под двумя именами). Сначала убедитесь, что на GPU нет процессов задания, например через `nvidia-smi`: команда ничего не проверяет и снимает резерв и удержания всех пользователей сразу.

   ```bash
   cy-queue gpu free 1
   ```

   ```text
   GPU 1: reservations and holds cleared
   ```

5. Поставьте задание в очередь заново ([`submit`](commands/submit.md)) и уберите старое в архив: `cy-queue archive job-17`.

## См. также

- [Указатель документации](README.md).
- [Глоссарий](../GLOSSARY.md).
