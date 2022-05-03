## YaTube ##
### Описание: ###
YaTube является аналогом LiveJournal и позволяет создавать пубикации,делиться ими в сообществах, подписываться на других пользователей и комментировать их публикации. Неавторизованные пользователи могут только читать публикации.

YaTube реализован на view-функциях чистого `Django 2.2.16` и имеет ользовательский интерфейс.

## Как запустить проект: ##

### Клонируйте репозиторий: ###

    git clone https://github.com/mark-rom/YaTube.git

### Перейдите в репозиторий в командной строке: ###
    cd YaTube

### Создайте и активируйте виртуальное окружение: ###
    python3.9 -m venv env

###### для Mac OS
    source env/bin/activate

###### для Windows OS
    source venv/Scripts/activate

### Установите зависимости из файла requirements.txt: ###
### Обновите pip:
    python3 -m pip install --upgrade pip

### Установите зависимости:
    pip install -r requirements.txt
  
### Выполните миграции: ###
    python3 manage.py migrate

### Запустить проект: ###
    python3 manage.py runserver
