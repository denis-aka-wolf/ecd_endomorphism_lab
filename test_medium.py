import os

def test_medium_scale():
    print("=== ТЕСТ 1: СРЕДНИЙ МАСШТАБ (12 БИТ) - ТАБЛИЧНЫЙ МЕТОД ===")
    
    # --- НАСТРОЙКИ ---
    BIT_WIDTH = 20          # 4096 вариантов
    P = 838861                # Модуль
    B = 17                   # Коэффициент
    C = 300                  # Константа
    # -----------------

    output_path = "medium_sat.cnf"
    clauses = []
    next_var = 1

    def alloc_var():
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    # Создаем биты X
    x_vars = [alloc_var() for _ in range(BIT_WIDTH)]
    
    def ban_pattern(bits):
        clause = []
        for i, val in enumerate(bits):
            var_id = x_vars[i]
            if val == 1: clause.append(f"-{var_id}")
            else: clause.append(f"{var_id}")
        clauses.append(" ".join(clause) + " 0")

    valid_solutions = []
    for x in range(1 << BIT_WIDTH):
        if (B * x + C) % P == 0:
            valid_solutions.append(x)
        else:
            bits = [(x >> i) & 1 for i in range(BIT_WIDTH)]
            ban_pattern(bits)

    if not valid_solutions:
        print("❌ ОШИБКА: Нет решений в диапазоне!")
        return

    print(f"✅ Найдено решений: {valid_solutions}")
    
    with open(output_path, "w") as f:
        f.write(f"p cnf {next_var - 1} {len(clauses)}\n")
        for clause in clauses:
            f.write(clause + "\n")

    print(f"📄 CNF создан: {output_path}")
    print(f"   Переменных: {next_var - 1}")
    print(f"   Клозов: {len(clauses)}")
    print("\n🚀 Запуск решателя (не забудь cryptominisat5 medium_sat.cnf)")

if __name__ == "__main__":
    test_medium_scale()
