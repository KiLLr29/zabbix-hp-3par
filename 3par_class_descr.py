#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import argparse
import logging
import logging.handlers
import pywbem

# Настройка логгера
LOG_FILENAME = "/tmp/hp_3par_class_discovery.log"
hp_logger = logging.getLogger("hp_3par_class_discovery_logger")
hp_logger.setLevel(logging.INFO)

# Устанавливаем хэндлер
hp_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=(1024**2)*10, backupCount=5)
hp_formatter = logging.Formatter('{asctime} - {name} - {levelname} - {message}', style='{')
hp_handler.setFormatter(hp_formatter)
hp_logger.addHandler(hp_handler)

def wbem_connect(hp_user, hp_password, hp_ip, hp_port, namespace):
    """
    Устанавливает соединение с WBEM-сервером.
    """
    try:
        wbem_url = f"https://{hp_ip}:{hp_port}"
        wbem_connection = pywbem.WBEMConnection(
            wbem_url,
            (hp_user, hp_password),
            default_namespace=namespace,
            no_verification=True,
            timeout=30
        )
        hp_logger.info(f"WBEM Connection Established Successfully for namespace: {namespace}")
        return wbem_connection
    except Exception as e:
        hp_logger.error(f"WBEM Connection Error Occurs: {e}")
        sys.exit("1000")

def get_classes(wbem_connection):
    """
    Получает список всех доступных CIM-классов в указанном пространстве имен,
    включая производные классы.
    """
    try:
        # Используем параметр DeepInheritance=True
        classes = wbem_connection.EnumerateClassNames(DeepInheritance=True)
        hp_logger.info("Successfully retrieved class names.")
        return sorted(classes)  # Возвращаем отсортированный список классов
    except Exception as e:
        hp_logger.error(f"Error retrieving class names: {e}")
        sys.exit("1000")

def get_instances_of_class(wbem_connection, class_name):
    """
    Получает все экземпляры указанного CIM-класса.
    """
    try:
        instances = wbem_connection.EnumerateInstances(class_name)
        hp_logger.info(f"Successfully retrieved instances for {class_name}")
        return instances
    except Exception as e:
        hp_logger.error(f"Error retrieving instances: {e}")
        sys.exit("1000")

def get_class_description(wbem_connection, class_name):
    """
    Получает описание CIM-класса.
    """
    try:
        class_obj = wbem_connection.GetClass(class_name, IncludeQualifiers=True, IncludeClassOrigin=True)
        hp_logger.info(f"Successfully retrieved class description for {class_name}")
        return class_obj
    except Exception as e:
        hp_logger.error(f"Error retrieving class description: {e}")
        sys.exit("1000")

def main():
    # Парсер аргументов командной строки
    parser = argparse.ArgumentParser(description="Discover available CIM classes in a namespace.")
    parser.add_argument('--hp_ip', action="store", required=True, help="IP address of the HP 3PAR system")
    parser.add_argument('--hp_port', action="store", default=5989, type=int, help="Port for WBEM connection (default: 5989)")
    parser.add_argument('--hp_user', action="store", required=True, help="Username for WBEM connection")
    parser.add_argument('--hp_password', action="store", required=True, help="Password for WBEM connection")
    parser.add_argument('--namespace', action="store", default="root/tpd", help="Namespace to query (default: root/tpd)")
    args = parser.parse_args()

    # Подключение к WBEM
    hp_logger.info("********************************* Class Discovery is starting *********************************")
    wbem_conn = wbem_connect(args.hp_user, args.hp_password, args.hp_ip, args.hp_port, args.namespace)

    # Получение списка классов
    classes = get_classes(wbem_conn)

    # Вывод результатов
    print(f"Available CIM classes in namespace '{args.namespace}':")
    for cls in classes:
        print(cls)

    hp_logger.info("********************************* Class Discovery is ended *********************************")
    
    class_description = get_class_description(wbem_conn, "TPD_FCPortLESBElementStatisticalData")
    instances = get_instances_of_class(wbem_conn, "TPD_FCPortLESBElementStatisticalData")
    
    # Выводим свойства класса
    print(f"Properties of TPD_FCPortLESBElementStatisticalData:")
    for prop_name, prop in class_description.properties.items():
        print(f"{prop_name}: {prop.type} ({prop.qualifiers})")

    # Выводим данные экземпляров
    for instance in instances:
        print(f"Instance of TPD_FCPortLESBElementStatisticalData:")
        for key, value in instance.items():
            print(f"  {key}: {value}")    

if __name__ == "__main__":
    main()
    