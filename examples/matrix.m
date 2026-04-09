A = eye(3);
B = ones(3);
C = A .+ B;
print C;

D = zeros(3);
D[0, 0] = 42;
# D[1:3, 2:4] = 7; # dla chetnych
print D;
print D[2, 2];
