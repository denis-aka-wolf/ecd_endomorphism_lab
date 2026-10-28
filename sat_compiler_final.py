import os

def compile_final_cnf():
    print("=== ФИНАЛЬНЫЙ CNF (ЖЕЛЕЗОБЕТОННАЯ ГАРАНТИЯ) ===")
    
    # --- НАСТРОЙКИ ---
    BIT_WIDTH = 8
    P = 257
    B = 5
    C = 10
    # -----------------

    output_path = "final_sat.cnf"
    clauses = []
    next_var = 1

    def alloc_var():
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    # 1. Создаем переменные для битов X (1..8)
    x_vars = [alloc_var() for _ in range(BIT_WIDTH)]
    
    # Функция, которая запрещает конкретную комбинацию битов
    # Если bits = [1, 0, 1...] (это значения, которые мы хотим ЗАПРЕТИТЬ)
    def ban_pattern(bits):
        clause = []
        for i, val in enumerate(bits):
            var_id = x_vars[i]
            # Если мы хотим запретить значение 1, пишем -var (чтобы var не мог быть 1)
            # Если мы хотим запретить значение 0, пишем var (чтобы var не мог быть 0)
            if val == 1:
                clause.append(f"-{var_id}")
            else:
                clause.append(f"{var_id}")
        clauses.append(" ".join(clause) + " 0")

    # 2. Перебираем ВСЕ возможные X от 0 до 255
    valid_solutions = []
    for x in range(1 << BIT_WIDTH):
        if (B * x + C) % P == 0:
            valid_solutions.append(x)
        else:
            # Для НЕ правильных решений добавляем запрет
            # Получаем биты числа x (младший бит первым, как в x_vars)
            bits = [(x >> i) & 1 for i in range(BIT_WIDTH)]
            ban_pattern(bits)

    if not valid_solutions:
        print("❌ ОШИБКА: Нет решений в диапазоне!")
        return

    print(f"✅ Найдено решений: {valid_solutions}")
    print(f"   Разрешены только эти значения X. Все остальные запрещены.")

    # Записываем файл
    with open(output_path, "w") as f:
        f.write("c =========================================================\n")
        f.write(f"c FINAL TABLE-BASED CNF\n")
        f.write(f"c Params: P={P}, B={B}, C={C}\n")
        f.write(f"c Valid X: {valid_solutions}\n")
        f.write("c =========================================================\n")
        f.write(f"p cnf {next_var - 1} {len(clauses)}\n")
        for clause in clauses:
            f.write(clause + "\n")

    print(f"📄 CNF создан: {output_path}")
    print(f"   Переменных: {next_var - 1}")
    print(f"   Клозов (запретов): {len(clauses)}")
    print("\n🚀 Запуск решателя:")
    print(f"   cryptominisat5 {output_path}")

if __name__ == "__main__":
    compile_final_cnf()
