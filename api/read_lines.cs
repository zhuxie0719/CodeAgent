using System;
using System.IO;
class Program {
    static void Main() {
        try {
            string[] lines = File.ReadAllLines(@"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251119_134538_571467_1f92395f\flask-2.0.0\src\flask\cli.py");
            for (int i = 819; i < 830 && i < lines.Length; i++) {
                Console.WriteLine($"{i+1}: {lines[i]}");
            }
        } catch (Exception e) {
            Console.WriteLine($"Error: {e.Message}");
        }
    }
}
