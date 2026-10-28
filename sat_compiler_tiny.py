import os

def compile_universal_cnf():
    print("=== УНИВЕРСАЛЬНЫЙ BIT-BLAST КОМПИЛЯТОР (Любые параметры) ===")
    
    # --- НАСТРОЙКИ (МЕНЯТЬ ЗДЕСЬ) ---
    BIT_WIDTH = 8          # Ширина x. Не ставь > 12, иначе CNF станет огромным.
    P = 257                # Модуль (простое или любое число)
    B = 5                  # Коэффициент при x
    C = 10                 # Константа
    # ---------------------------------

    output_path = "universal_sat.cnf"
    clauses = []
    next_var = 1

    def alloc_var():
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    # === БАЗОВЫЕ ВЕНТИЛИ ===
    
    # AND: res = a & b
    def add_and(res, a, b):
        clauses.append(f"-{res} {a} 0")
        clauses.append(f"-{res} {b} 0")
        clauses.append(f"{res} -{a} -{b} 0")

    # XOR: res = a ^ b
    def add_xor(res, a, b):
        clauses.append(f"-{res} -{a} -{b} 0")
        clauses.append(f"-{res} {a} {b} 0")
        clauses.append(f"{res} -{a} {b} 0")
        clauses.append(f"{res} {a} -{b} 0")

    # Full Adder: (sum, carry_out) = FA(a, b, carry_in)
    def get_full_adder(a, b, cin):
        s_out = alloc_var()
        c_out = alloc_var()
        tmp = alloc_var()
        
        # Sum = a ^ b ^ cin
        add_xor(tmp, a, b)
        add_xor(s_out, tmp, cin)

        # Carry = (a & b) | (cin & (a ^ b))
        and1 = alloc_var(); add_and(and1, a, b)
        and2 = alloc_var(); add_and(and2, cin, tmp)
        
        # OR для carry: c_out = and1 OR and2
        clauses.append(f"-{c_out} {and1} 0")
        clauses.append(f"-{c_out} {and2} 0")
        clauses.append(f"{c_out} -{and1} -{and2} 0")
        
        return s_out, c_out

    # === ФУНКЦИЯ СЛОЖЕНИЯ ДВУХ НАБОРОВ БИТ ===
    # Принимает списки переменных (или констант 0/1) и возвращает список переменных суммы
    def add_bit_arrays(a_vars, a_consts, b_vars, b_consts):
        len_a = len(a_vars)
        len_b = len(b_vars)
        max_len = max(len_a, len_b)
        
        res_vars = []
        carry = alloc_var()
        clauses.append(f"-{carry} 0")  # Инициализация carry = 0

        for i in range(max_len + 1):
            # Получаем операнды для текущего разряда i
            val_a_var = a_vars[i] if i < len_a else None
            val_a_const = a_consts[i] if i < len(a_consts) else 0
            
            val_b_var = b_vars[i] if i < len_b else None
            val_b_const = b_consts[i] if i < len(b_consts) else 0

            # Нормализуем входы: если есть переменная - берем её, если нет - константа
            if val_a_var is not None:
                inp_a = val_a_var
            else:
                # Константа 1 -> переменная принудительно TRUE, 0 -> FALSE
                if val_a_const == 1:
                    inp_a = alloc_var()
                    clauses.append(f"{inp_a} 0")
                else:
                    inp_a = alloc_var()
                    clauses.append(f"-{inp_a} 0")

            if val_b_var is not None:
                inp_b = val_b_var
            else:
                if val_b_const == 1:
                    inp_b = alloc_var()
                    clauses.append(f"{inp_b} 0")
                else:
                    inp_b = alloc_var()
                    clauses.append(f"-{inp_b} 0")

            s, new_carry = get_full_adder(inp_a, inp_b, carry)
            res_vars.append(s)
            carry = new_carry
            
        return res_vars, carry

    # === 1. ПЕРЕМЕННЫЕ ДЛЯ x ===
    x_vars = [alloc_var() for _ in range(BIT_WIDTH)]
    x_consts = [0] * BIT_WIDTH  # x - это переменные, констант нет

    # === 2. СХЕМА B * x ===
    # B - константа. B*x = сумма сдвинутых копий x там, где в B есть единицы.
    shifts = []
    for i in range(BIT_WIDTH + 2): # B может быть чуть больше BIT_WIDTH
        if (B >> i) & 1:
            shifts.append(i)
    
    if not shifts:
        # Если B=0, то B*x = 0. Создадим массив нулей.
        Bx_vars = []
        for _ in range(BIT_WIDTH * 2 + 2):
            v = alloc_var()
            clauses.append(f"-{v} 0") # 0
            Bx_vars.append(v)
    else:
        # Берем первый сдвиг как базу
        first_shift = shifts[0]
        base_len = BIT_WIDTH + first_shift + 1
        current_sum_vars = [None] * base_len
        current_sum_consts = [0] * base_len
        
        # Заполняем базу (первый частичный продукт)
        for i in range(BIT_WIDTH):
            pos = i + first_shift
            if pos < base_len:
                current_sum_vars[pos] = x_vars[i]
        
        # Складываем остальные частичные продукты
        for k in range(1, len(shifts)):
            shift = shifts[k]
            next_sum_vars = [None] * (BIT_WIDTH + shift + 1)
            next_sum_consts = [0] * len(next_sum_vars)
            
            for i in range(BIT_WIDTH):
                pos = i + shift
                if pos < len(next_sum_vars):
                    next_sum_vars[pos] = x_vars[i]
            
            # Складываем current_sum + next_sum
            # Нам нужно расширить массивы до одинаковой длины для функции
            # Функция сама обработает разную длину, передадим ей текущие списки
            # Но нам нужно привести current_sum к новому размеру
            extended_vars = current_sum_vars + [None]*(len(next_sum_vars)-len(current_sum_vars))
            extended_consts = current_sum_consts + [0]*(len(next_sum_consts)-len(current_sum_consts))
            
            current_sum_vars, _ = add_bit_arrays(extended_vars, extended_consts, next_sum_vars, next_sum_consts)
            # Обновляем длину констант (они все 0, так как складываем переменные)
            current_sum_consts = [0] * len(current_sum_vars)

        Bx_vars = current_sum_vars
        # Дополним нулями, если вдруг длина меньше ожидаемой (для выравнивания)
        while len(Bx_vars) < BIT_WIDTH * 2 + 2:
             v = alloc_var()
             clauses.append(f"-{v} 0")
             Bx_vars.append(v)

    # === 3. СХЕМА (B*x) + C ===
    C_bits = [(C >> i) & 1 for i in range(len(Bx_vars))]
    LHS_vars, overflow_LHS = add_bit_arrays(Bx_vars, C_bits, [], [])
    # Overflow игнорируем или можно добавить проверку, что он 0, если хотим строгое равенство без переполнения
    
    # === 4. СХЕМА k * P ===
    # k - неизвестное, такое же широкое, как x (примерно)
    k_width = BIT_WIDTH + 2 # k может быть чуть шире
    k_vars = [alloc_var() for _ in range(k_width)]
    k_consts = [0] * k_width
    
    P_bits = [(P >> i) & 1 for i in range(k_width + 2)]
    p_shifts = [i for i, bit in enumerate(P_bits) if bit == 1]
    
    if not p_shifts:
        kP_vars = [alloc_var() for _ in range(k_width * 2)]
        for v in kP_vars: clauses.append(f"-{v} 0")
    else:
        # Аналогично умножению B*x, но теперь множитель - переменная k
        first_shift = p_shifts[0]
        base_len = k_width + first_shift + 1
        current_kP_vars = [None] * base_len
        current_kP_consts = [0] * base_len
        
        for i in range(k_width):
            pos = i + first_shift
            if pos < base_len:
                current_kP_vars[pos] = k_vars[i]
        
        for k_idx in range(1, len(p_shifts)):
            shift = p_shifts[k_idx]
            next_kP_vars = [None] * (k_width + shift + 1)
            next_kP_consts = [0] * len(next_kP_vars)
            for i in range(k_width):
                pos = i + shift
                if pos < len(next_kP_vars):
                    next_kP_vars[pos] = k_vars[i]
            
            ext_vars = current_kP_vars + [None]*(len(next_kP_vars)-len(current_kP_vars))
            ext_consts = current_kP_consts + [0]*(len(next_kP_consts)-len(current_kP_consts))
            
            current_kP_vars, _ = add_bit_arrays(ext_vars, ext_consts, next_kP_vars, next_kP_consts)
            current_kP_consts = [0] * len(current_kP_vars)
        
        kP_vars = current_kP_vars
        while len(kP_vars) < len(LHS_vars):
            v = alloc_var()
            clauses.append(f"-{v} 0")
            kP_vars.append(v)

    # Выравниваем длины для сравнения
    max_comp_len = max(len(LHS_vars), len(kP_vars))
    while len(LHS_vars) < max_comp_len:
        v = alloc_var()
        clauses.append(f"-{v} 0")
        LHS_vars.append(v)
    while len(kP_vars) < max_comp_len:
        v = alloc_var()
        clauses.append(f"-{v} 0")
        kP_vars.append(v)

    # === 5. УСЛОВИЕ РАВЕНСТВА: LHS == RHS (k*P) ===
    for i in range(max_comp_len):
        l = LHS_vars[i]
        r = kP_vars[i]
        # l <-> r  =>  (-l OR r) AND (l OR -r)
        clauses.append(f"-{l} {r} 0")
        clauses.append(f"{l} -{r} 0")

    # === ЗАПИСЬ CNF ===
    with open(output_path, "w") as f:
        f.write("c =========================================================\n")
        f.write(f"c UNIVERSAL BIT-BLAST CNF: B*x + C == k*P (mod P)\n")
        f.write(f"c Params: W={BIT_WIDTH}, P={P}, B={B}, C={C}\n")
        f.write("c =========================================================\n")
        f.write(f"p cnf {next_var - 1} {len(clauses)}\n")
        for clause in clauses:
            f.write(clause + "\n")

    print(f"✅ CNF создан: {output_path}")
    print(f"   Переменных: {next_var - 1}")
    print(f"   Клозов: {len(clauses)}")
    
    # Проверка ожидаемого решения (для себя)
    found_x = None
    limit = 1 << BIT_WIDTH
    for x_test in range(limit):
        val = (B * x_test + C)
        if val % P == 0:
            found_x = x_test
            k_test = val // P
            break
    
    if found_x is not None:
        print(f"\n🎯 Ожидаемое решение: x = {found_x} (bin: {bin(found_x)[2:].zfill(BIT_WIDTH)})")
        print(f"   k = {k_test}")
    else:
        print("\n⚠️ Внимание: Для этих параметров нет решения в диапазоне 0..2^BIT_WIDTH-1.")
        print("   Попробуй изменить B, C или P.")

if __name__ == "__main__":
    compile_universal_cnf()
