import sys
sys.stdout.reconfigure(encoding='utf-8')  # Добавь эту строку в начало

print("Введите первое число:", flush=True)
a = int(input())
print("Введите второе число:", flush=True)
b = int(input())
print("Результат:", a + b, flush=True)