def compile_huge_gates_fixed():
    print("=== ТЕСТ 3: ИСПРАВЛЕННАЯ СХЕМА (20 БИТ) ===")
    
    # --- НАСТРОЙКИ ---
    BIT_WIDTH = 18  # 18 бит хватит, т.к. P ~ 100k (2^17 = 131k)
    P = 100003
    B = 5
    C = 10
    # -----------------
    
    output_path = "huge_sat_fixed.cnf"
    clauses = []
    next_var = 1

    def alloc_var():
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    # AND(a, b) -> res
    def gate_and(res, a, b):
        clauses.append(f"-{res} {a} 0")
        clauses.append(f"-{res} {b} 0")
        clauses.append(f"{res} -{a} -{b} 0") # Если a=0 или b=0, то res=0
        clauses.append(f"-{a} -{b} {res} 0") # Если a=1 и b=1, то res=1

    # XOR(a, b) -> res
    def gate_xor(res, a, b):
        # Таблица истинности: 00->0, 01->1, 10->1, 11->0
        clauses.append(f"-{res} -{a} -{b} 0")
        clauses.append(f"-{res} {a} {b} 0")
        clauses.append(f"{res} -{a} {b} 0")
        clauses.append(f"{res} {a} -{b} 0")

    # Полный сумматор: sum_bit = a ^ b ^ cin, carry_out = (a & b) | (cin & (a ^ b))
    def full_adder(sum_bit, carry_out, a, b, carry_in):
        ab_xor = alloc_var()
        gate_xor(ab_xor, a, b)
        
        gate_xor(sum_bit, ab_xor, carry_in)
        
        and1 = alloc_var(); gate_and(and1, a, b)
        and2 = alloc_var(); gate_and(and2, ab_xor, carry_in)
        
        # carry_out = and1 OR and2
        clauses.append(f"-{and1} {carry_out} 0")
        clauses.append(f"-{and2} {carry_out} 0")
        clauses.append(f"{and1} {and2} -{carry_out} 0")

    # Сложение двух списков битов (результат может быть на 1 бит длиннее)
    def add_arrays(bits_a, bits_b):
        max_len = max(len(bits_a), len(bits_b))
        res = []
        carry = alloc_var()
        clauses.append(f"-{carry} 0") # Начальный перенос 0
        
        for i in range(max_len):
            a_val = bits_a[i] if i < len(bits_a) else alloc_var(); 
            if i >= len(bits_a): clauses.append(f"-{a_val} 0") # Явно ставим 0
            
            b_val = bits_b[i] if i < len(bits_b) else alloc_var();
            if i >= len(bits_b): clauses.append(f"-{b_val} 0") # Явно ставим 0
            
            s_bit = alloc_var()
            next_carry = alloc_var()
            full_adder(s_bit, next_carry, a_val, b_val, carry)
            res.append(s_bit)
            carry = next_carry
        
        return res, carry

    # Умножение числа (массив битов) на константу через сдвиги
    def mul_by_const(bits, const_val):
        parts = []
        # Проходим по битам константы
        for shift in range(const_val.bit_length()):
            if (const_val >> shift) & 1:
                # Создаем массив длиной len(bits) + shift
                shifted = [alloc_var() for _ in range(len(bits) + shift)]
                
                # Заполняем младшие биты нулями (сдвиг)
                for i in range(shift):
                    clauses.append(f"-{shifted[i]} 0")
                
                # Копируем биты: shifted[i+shift] = bits[i]
                for i in range(len(bits)):
                    src = bits[i]
                    dst = shifted[i + shift]
                    # src -> dst
                    clauses.append(f"-{src} {dst} 0")
                    # dst -> src
                    clauses.append(f"-{dst} {src} 0")
                parts.append(shifted)
        
        if not parts:
            return [alloc_var()] # Возврат 0
            
        total = parts[0]
        for i in range(1, len(parts)):
            total, _ = add_arrays(total, parts[i])
        return total

    # === ГЛАВНАЯ ЛОГИКА ===
    
    # 1. Переменные X
    x_vars = [alloc_var() for _ in range(BIT_WIDTH)]
    
    # 2. Вычисляем B * x
    bx_bits = mul_by_const(x_vars, B)
    
    # 3. Вычисляем C (константа) как битовый массив
    c_bits = []
    temp_c = C
    # Длина C должна быть хотя бы такой же, как у bx_bits, чтобы корректно сложить
    for i in range(len(bx_bits) + 2):
        bit_val = 1 if (temp_c & 1) else 0
        var = alloc_var()
        if bit_val == 1: clauses.append(f"{var} 0")
        else: clauses.append(f"-{var} 0")
        c_bits.append(var)
        temp_c >>= 1
    
    # 4. LHS = B*x + C
    lhs_bits, lhs_overflow = add_arrays(bx_bits, c_bits)
    
    # 5. RHS = k * P (подбираем k так, чтобы покрыть диапазон)
    # Максимальное значение LHS примерно: B * 2^20 + C ~ 17 млн.
    # P = 838k. Значит k может быть до ~20. Возьмем 6 бит для k (хватит до 63).
    K_WIDTH = 6
    k_vars = [alloc_var() for _ in range(K_WIDTH)]
    kp_bits = mul_by_const(k_vars, P)
    
    # 6. Выравнивание длин для сравнения
    max_len = max(len(lhs_bits), len(kp_bits))
    
    while len(lhs_bits) < max_len:
        v = alloc_var(); clauses.append(f"-{v} 0"); lhs_bits.append(v)
    while len(kp_bits) < max_len:
        v = alloc_var(); clauses.append(f"-{v} 0"); kp_bits.append(v)
        
    # 7. Сравнение битов: lhs_i == kp_i
    for i in range(max_len):
        a = lhs_bits[i]
        b = kp_bits[i]
        clauses.append(f"-{a} {b} 0")
        clauses.append(f"-{b} {a} 0")
    
    # 8. Переполнение LHS должно быть 0 (иначе оно больше любого k*P)
    clauses.append(f"-{lhs_overflow} 0")

    with open(output_path, "w") as f:
        f.write(f"p cnf {next_var - 1} {len(clauses)}\n")
        for c in clauses:
            f.write(c + "\n")
            
    print(f"✅ CNF создан: {output_path}")
    print(f"   Переменных: {next_var - 1}")
    print(f"   Клозов: {len(clauses)}")
    print(f"\n🚀 Параметры: P={P}, B={B}, C={C}")

if __name__ == "__main__":
    compile_huge_gates_fixed()
