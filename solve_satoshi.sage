# Файл solve_satoshi.sage
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
R.<x> = PolynomialRing(GF(P))

# Это точные коэффициенты из вашего файла genesis_satoshi_system.anf
A = 0x2281e25a6598881f570f10ef03294c03fd46018ac75af0a1092db5fb5f1b750b
B = 0x3b9364a918ebb5452f0911328b1782d67d6926206dfb9631d49fd3436f021702
C = 0x38ed0bc25afd20a3003eda4fc3dfd1d1f5ed491d8e062d60b91bf35c04f8a494

f = A*x^2 + B*x + C
print("Поиск корней полинома Семаева Сатоши...")
print(f.roots())
