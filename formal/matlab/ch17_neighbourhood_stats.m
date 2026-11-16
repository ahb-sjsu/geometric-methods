% ch17_neighbourhood_stats.m
% Symbolic and numerical checks for Section 17.11 of Geometric Methods
% (Neighbourhood Statistics in High Dimension). Needs the Symbolic Math
% Toolbox. Run:  matlab -batch "run('ch17_neighbourhood_stats.m')"
% Each check prints PASS or FAIL; the last line is the tally.

npass = 0; nfail = 0;

syms L positive          % Poisson mean
syms c integer
pmf = exp(-L) * L^c / factorial(c);
r1 = simplify(symsum(c   * pmf, c, 0, inf));
r2 = simplify(symsum(c^2 * pmf, c, 0, inf));
r3 = simplify(symsum(c^3 * pmf, c, 0, inf));

% (17.6) skewness of a Poisson count is 1/sqrt(rho)
varP = simplify(r2 - r1^2);
mu3P = simplify(r3 - 3*r1*r2 + 2*r1^3);
[npass, nfail] = report('Poisson mean = L', r1 - L, npass, nfail);
[npass, nfail] = report('Poisson variance = L', varP - L, npass, nfail);
[npass, nfail] = report('Poisson third central moment = L', mu3P - L, npass, nfail);
[npass, nfail] = report('(17.6) Poisson skewness = 1/sqrt(L)', ...
    mu3P / varP^(3/2) - 1/sqrt(L), npass, nfail);

% (17.7), (17.8): count | w ~ Poisson(rho*w), E[w] = 1.
% m2, m3 are the raw second and third moments of w.
syms rho positive
syms w m2 m3 real
e1 = subs(r1, L, rho*w);            % E[c | w]
e2 = subs(r2, L, rho*w);            % E[c^2 | w]
e3 = subs(r3, L, rho*w);            % E[c^3 | w]
Ew = @(p) subs(subs(subs(expand(p), w^3, m3), w^2, m2), w, 1);   % E over w
E1 = Ew(e1); E2 = Ew(e2); E3 = Ew(e3);
varC = simplify(E2 - E1^2);
mu3C = simplify(E3 - 3*E1*E2 + 2*E1^3);
varW = m2 - 1;                       % Var(w) with mean one
mu3W = m3 - 3*m2 + 2;                % third central moment of w
[npass, nfail] = report('mean count = rho', E1 - rho, npass, nfail);
[npass, nfail] = report('(17.7) Var(N) = rho + rho^2 Var(w)', ...
    varC - (rho + rho^2*varW), npass, nfail);
[npass, nfail] = report('(17.8) mu3(N) = rho + 3 rho^2 Var(w) + rho^3 mu3(w)', ...
    mu3C - (rho + 3*rho^2*varW + rho^3*mu3W), npass, nfail);

% (17.9) the inversion
[npass, nfail] = report('(17.9) Var(w) = (Var(N) - rho)/rho^2', ...
    (varC - rho)/rho^2 - varW, npass, nfail);
[npass, nfail] = report('(17.9) mu3(w) = (mu3(N) - 3 Var(N) + 2 rho)/rho^3', ...
    (mu3C - 3*varC + 2*rho)/rho^3 - mu3W, npass, nfail);

% The line of hubness.py: mu3_w = (mu3(N) - rho - 3 rho^2 var_w)/rho^3
[npass, nfail] = report('hubness.py form of mu3(w) agrees with (17.9)', ...
    (mu3C - rho - 3*rho^2*varW)/rho^3 - mu3W, npass, nfail);

% (17.1), (17.2): P(mu > t) = t^(-d)  =>  ln(mu) is exponential, rate d;
% the likelihood equation gives d = N / sum(ln mu).
syms d positive
syms t s positive
[npass, nfail] = report('(17.1) ln(mu) has survival exp(-d s)', ...
    subs(t^(-d), t, exp(s)) - exp(-d*s), npass, nfail);
syms N S positive                    % N points, S = sum of ln(mu_i)
loglik = N*log(d) - d*S;             % exponential log-likelihood
dhat = solve(diff(loglik, d) == 0, d);
[npass, nfail] = report('(17.2) MLE d = N / sum(ln mu)', dhat - N/S, npass, nfail);

% (17.3): mean of an Exp(d) variable cut at its q-quantile
syms q positive
assumeAlso(q < 1);
x = sym('x', 'positive');
tq = -log(1 - q)/d;                  % q-quantile of Exp(d)
mtrunc = simplify(int(x * d*exp(-d*x), x, 0, tq) / q);
target = (1/d) * (1 + (1 - q)*log(1 - q)/q);
[npass, nfail] = report('(17.3) truncated mean', mtrunc - target, npass, nfail);
factor = double(subs(1/(1 + (1 - q)*log(1 - q)/q), q, sym(9)/10));
fprintf('trim factor at q = 0.9: %.6f\n', factor);
ok = abs(factor - 1.344) < 5e-4;
[npass, nfail] = reportb('(17.3) factor rounds to 1.344', ok, npass, nfail);

% Monte Carlo of the trimmed estimator, coded as in geometry.id_twonn
rng(20261115);
dtrue = 20; M = 2e6;
mu = rand(M, 1).^(-1/dtrue);         % Pareto, shape dtrue
mu = mu(mu > 1);
mu = mu(mu <= quantile(mu, 0.9));
dhat_mc = numel(mu) / sum(log(mu));
fprintf('Monte Carlo: d = %d, trimmed estimate %.4f, ratio %.5f\n', ...
    dtrue, dhat_mc, dhat_mc/dtrue);
ok = abs(dhat_mc/dtrue - factor) < 5e-3;
[npass, nfail] = reportb('trimmed estimator reads factor*d (Monte Carlo)', ok, npass, nfail);

% The count in the text: 16000^(1/52) points per dimension
ppd = 16000^(1/52);
fprintf('16000^(1/52) = %.4f\n', ppd);
[npass, nfail] = reportb('16000^(1/52) rounds to 1.2', abs(ppd - 1.2) < 0.05, npass, nfail);

% Table arithmetic of 17.11.2: rho = n_q k / n and the last-cell null
nq = 10000; k = 10; n = [25000 50000 100000 200000];
rhos = nq*k ./ n;
[npass, nfail] = reportb('rho row = 4, 2, 1, 0.5', isequal(rhos, [4 2 1 0.5]), npass, nfail);
[npass, nfail] = reportb('1.79 / (1/sqrt(0.5)) rounds to 1.27', ...
    abs(1.79*sqrt(0.5) - 1.27) < 5e-3, npass, nfail);

fprintf('TALLY: %d PASS, %d FAIL\n', npass, nfail);

function [np, nf] = report(name, expr, np, nf)
    ok = isAlways(simplify(expr) == 0, 'Unknown', 'false');
    [np, nf] = reportb(name, ok, np, nf);
end

function [np, nf] = reportb(name, ok, np, nf)
    if ok
        fprintf('PASS  %s\n', name); np = np + 1;
    else
        fprintf('FAIL  %s\n', name); nf = nf + 1;
    end
end
