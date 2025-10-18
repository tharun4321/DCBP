import java.util.Scanner;

public class UserInputExample {
    public static void main(String[] args) {
        // Create Scanner object to take input
        Scanner sc = new Scanner(System.in);

        // Ask user for input
        System.out.print("Enter your name: ");
        String name = sc.nextLine();  // Takes string input

        System.out.print("Enter your age: ");
        int age = sc.nextInt();  // Takes integer input

        // Print the input values
        System.out.println("\n--- User Details ---");
        System.out.println("Name: " + name);
        System.out.println("Age: " + age);

        sc.close();  // Close scanner to prevent resource leak
    }
}
