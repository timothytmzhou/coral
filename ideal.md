func gcd(a, b) {
    while b {
        tmp = b;
        b = a % b;
        a = tmp;
    }
    return a;
}
i = 1; while i < 10 do i++; {
    print(gcd(50, i));
}
