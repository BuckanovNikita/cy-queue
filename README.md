# cy-queue

`cy-queue` — [очередь (queue)](GLOSSARY.md#queue) [заданий (job)](GLOSSARY.md#job) на целые GPU для команд [clearml-yolo](https://github.com/BuckanovNikita/clearml-yolo) (CY) `cy` и `cy-train`. Вы ставите команду CY в очередь, а ваш [worker](GLOSSARY.md#worker) запускает её, когда освобождается нужное число GPU. Очередь нужна ML-инженерам, которые делят один GPU-хост с другими пользователями Linux. Команды `cy` и `cy-train` работают и без очереди; очередь нужна, только чтобы планировать запуски.

Требования: Linux, Python `>=3.12.13,<3.14`, `clearml-yolo>=0.38` в том же окружении, GPU NVIDIA.

## Установка

`cy-queue` ставится из исходников в окружение CY:

```bash
git clone https://github.com/BuckanovNikita/cy-queue.git /path/to/cy-queue
uv pip install --python /path/to/clearml-yolo/.venv/bin/python -e /path/to/cy-queue
```

Настройка хоста и `queue.toml` — в [Подготовке хоста](docs/setup.md).

## Первое задание

```bash
cy-queue config
cy-queue worker                      # в отдельном терминале
cy-queue submit --gpus 1 -- ground_truth=data/ground_truth.csv
cy-queue list
```

Подробно, с выводом и поиском журнала задания, — в [первом сценарии](docs/scenarios.md#1-первый-запуск).

## Подкоманды

| Подкоманда | Что делает |
| --- | --- |
| [`config`](docs/commands/config.md) | Печатает настройки очереди. |
| [`submit`](docs/commands/submit.md) | Ставит в очередь команду CY или Hydra sweep. |
| [`worker`](docs/commands/worker.md) | Запускает ваши задания на GPU хоста. |
| [`list`](docs/commands/list.md) | Печатает очередь: состояния, GPU, причины ожидания. |
| [`tui`](docs/commands/list.md#cy-queue-tui) | Интерактивный [вид очереди (queue view)](GLOSSARY.md#queue-view) в терминале. |
| [`move`](docs/commands/jobs.md#move) | Меняет порядок ожидающих заданий. |
| [`cancel`](docs/commands/jobs.md#cancel) | Отменяет задание. |
| [`recover`](docs/commands/jobs.md#recover) | Освобождает задание в `recovery_required`: останавливает оставшиеся процессы и снимает резерв. |
| [`archive`](docs/commands/jobs.md#archive) | Убирает завершённые задания в архив. |
| [`restore`](docs/commands/jobs.md#restore) | Возвращает задания из архива. |
| [`gpu list`](docs/commands/gpu.md#gpu-list) | Показывает GPU хоста, удержания и резервы. |
| [`gpu disable`](docs/commands/gpu.md#gpu-disable) | Ставит ваше удержание на GPU. |
| [`gpu enable`](docs/commands/gpu.md#gpu-enable) | Снимает ваше удержание с GPU. |
| [`gpu free`, `gpu release`](docs/commands/gpu.md#gpu-free-и-gpu-release) | Снимает с GPU резерв и все удержания. |

## Дальше

- [Указатель документации](docs/README.md).
- [Глоссарий](GLOSSARY.md).
- [Репозиторий CY](https://github.com/BuckanovNikita/clearml-yolo) — команды и конфигурация CY.
