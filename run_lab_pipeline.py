import sys
import subprocess
import os

def run_script_transparent(script_name):
    """Абсолютно прозрачный запуск дочерних скриптов с прямым выводом в консоль."""
    python_exe = sys.executable
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    print(f"\n[Запуск модуля]: {script_name}...")
    print("-" * 60)
    
    # Мы убираем capture_output, чтобы операционная система сама печатала 
    # любые ошибки, включая синтаксические (SyntaxError) и отсутствующие переменные.
    result = subprocess.run(
        [python_exe, script_path],
        check=False # Не падаем молча, даем конвейеру идти дальше для сбора логов
    )
    
    if result.returncode != 0:
        print(f"⚠️ Модуль {script_name} завершился с системным кодом ошибки: {result.returncode}")

def main():
    print("=" * 70)
    print("🔎 РЕЖИМ ОТЛАДКИ И СКВОЗНОЙ ДИАГНОСТИКИ КОНВЕЙЕРА СЕМАЕВА F4")
    print("=" * 70)
    
    run_script_transparent("toy_curve.py")
    run_script_transparent("secp256k1_solver.py")
    run_script_transparent("semaev_f4_solver.py")
    run_script_transparent("anf_exporter.py")
    run_script_transparent("sat_compiler.py")
    run_script_transparent("solve_f4_resultant.py")
    run_script_transparent("bit_deductor.py")
    run_script_transparent("verify_solution.py")
    run_script_transparent("run_solver_cluster.py")
    
    print("=" * 70)
    print("🏁 Диагностический проход завершен.")
    print("=" * 70)

if __name__ == "__main__":
    main()
