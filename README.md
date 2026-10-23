# cy-queue

Отдельная очередь для `clearml-yolo`: постоянные задания, процессы от имени владельца,
резервирование целых NVIDIA GPU, отмена, восстановление и терминальный интерфейс.
Команды `cy` и `cy-train` работают самостоятельно; очередь нужна только для
явного планирования запусков.

## Установка из исходников

Требуются Linux с поддержкой pidfd/subreaper и Python в диапазоне из
[pyproject.toml](pyproject.toml). Установите совместимый CY из исходников,
подготовив его утверждённые внешние зависимости по инструкции проекта. Затем
установите эту очередь **в то же окружение**. Публикация пакетов в PyPI не предполагается.

```bash
uv pip install --python /path/to/environment/bin/python /path/to/clearml-yolo
uv pip install --python /path/to/environment/bin/python /path/to/cy-queue
/path/to/environment/bin/cy-queue --help
```

Для изолированной сети заранее подготовьте все зависимости в доступном локальном
индексе или окружении. Очередь не устанавливает зависимости и не меняет их исходники.
При уже подготовленных зависимостях допустима установка исходников с `--no-deps`;
совместимость версий всё равно нужно проверить. Textual и NVML принадлежат очереди.

## Конфигурация и запуск

Укажите одинаковые общие каталоги у всех пользователей. Метаданные очереди и
локальная координация — разные хранилища; каталог координации должен обеспечивать
проверенные локальные блокировки. Существующие пути и имена блокировок сохранены.

Создайте `$HOME/.config/clearml-yolo/queue.toml` или укажите файл через `CY_QUEUE_CONFIG`.
При абсолютном непустом `XDG_CONFIG_HOME` используется
`$XDG_CONFIG_HOME/clearml-yolo/queue.toml`.

```toml
[queue]
name = "Training"
root = "/srv/training/queue"
coordination_root = "/var/lib/training/coordination"
```

```bash
cy-queue config
cy-queue submit --gpus 1 -- ground_truth=dataset.csv ultralytics.model=yolo11n.pt
cy-queue submit --command train --gpus 1 -- ground_truth=dataset.csv ultralytics.model=yolo11n.pt
cy-queue worker
cy-queue list --json
cy-queue tui
```

Без `--command` запускается `pipeline`; `--command train` запускает существующий
`cy-train`. После `--` передаются параметры Hydra; без `--config-name` выбирается
корень соответствующей команды. Файл конфигурации должен соответствовать этой команде.
Пакетный запуск `-m` проверяется целиком до записи заданий. Разрешены `--gpus` либо
`--devices`; GPU-параметры нативной модели задаёт очередь, явные CPU-фазы сохраняются.

Рабочий процесс запускает только задания своего Unix-пользователя. История,
владение, отмена, восстановление и подтверждённая передача GPU сохраняют прежние
контракты CY. Успех вычисления не доказывает завершение очистки процессов.

- [Обновление без потери записей](docs/migration.md)
- [Граница CY и очереди](docs/interfaces.md)
- [Разработка и проверки](docs/development.md)
- [Контракт операций CY](https://github.com/BuckanovNikita/clearml-yolo/blob/master/docs/queue.md)
