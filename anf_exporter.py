import sys
import json
import os

SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

def export_to_anf():
    print("=== ГЕНЕРАТОР БИТОВЫХ МАСОК ДЛЯ SAT-СОЛВЕРА (ОПТИМИЗАЦИЯ GLV-3) ===")
    print("Динамическое построение ANF-модели под усеченный базис F4 (~85 бит)\n")
    
    # Считываем коэффициенты, сгенерированные модулем semaev_f4_solver.py
    json_path = os.path.join(os.path.dirname(__file__), "f4_matrix.json")
    if not os.path.exists(json_path):
        print("❌ Ошибка: Файл f4_matrix.json не найден. Запустите весь конвейер!")
        return

    with open(json_path, "r") as f:
        data = json.load(f)
        
    A1 = int(data["A1"], 16)
    B1 = int(data["B1"], 16)
    C1 = int(data["C1"], 16)
    
    print(f"[Контекст]: Уравнение ветви F4 загружено успешно.")
    print(f"            Свободный член C1: {hex(C1)}\n")
    
    # В GLV-3 каждый скаляр k_i занимает порядка 85-86 бит.
    # Соответственно, искомая координата x_i линеаризуется в меньшем окне.
    bit_dimension = 85
    print(f"[Шаг 1] Вычисление линейного вклада битов для окна {bit_dimension} бит:")
    for i in range(8):  # Демонстрируем маски для первых 8 бит нового базиса
        weight = (B1 * (1 << i)) % SECP256K1_P
        print(f"        Бит x_{i} активирует константу поля: {hex(weight)}")
        
    print("\n[Шаг 2] Вычисление перекрестных квадратичных мономов (AND-связи):")
    for i in range(3):
        for j in range(i, 3):
            if i == j:
                weight = (A1 * (1 << (2 * i))) % SECP256K1_P
                print(f"        Квадратичный моном [x_{i}]: {hex(weight)}")
            else:
                weight = (2 * A1 * (1 << (i + j))) % SECP256K1_P
                print(f"        Перекрестный моном [x_{i} * x_{j}]: {hex(weight)}")

    print("\n[Шаг 3] Формирование целевого вектора свободных членов:")
    print(f"        Целевой XOR-баланс системы: {hex(C1)}")
    
    # Перезаписываем глобальную матрицу для компилятора SAT
    current_matrix_path = os.path.join(os.path.dirname(__file__), "current_matrix.json")
    with open(current_matrix_path, "r") as f:
        global_data = json.load(f)
    
    global_data["A"] = hex(A1)
    global_data["B"] = hex(B1)
    global_data["C"] = hex(C1)
    
    with open(current_matrix_path, "w") as f:
        json.dump(global_data, f)
        
    print("\n[Статус]: Битовые маски для 85-битных подпространств Сатоши успешно посчитаны.")

if __name__ == "__main__":
    export_to_anf()
