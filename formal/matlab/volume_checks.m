% volume_checks.m
% Symbolic and numerical checks behind the 2026-11 corrections to
% Geometric Methods (chapters 2, 6, 9, 10, 11, 13, 19; appendix C).
% Needs the Symbolic Math Toolbox.
% Run:  matlab -batch "run('volume_checks.m')"

npass = 0; nfail = 0;

%% Chapters 2 and 11: the 20-point log grid on [0.01, 100]
g = logspace(-2, 2, 20);
fprintf('grid head: %s\n', mat2str(g(1:5), 3));
fprintf('grid tail: %s\n', mat2str(g(end-4:end), 3));
step20 = 10^(4/19); step50 = 10^(4/49);
fprintf('step n=20: %.4f   step n=50: %.4f\n', step20, step50);
[npass, nfail] = reportb('grid step for n = 20 rounds to 1.62', abs(step20 - 1.62) < 5e-3, npass, nfail);
[npass, nfail] = reportb('grid step for n = 50 rounds to 1.21', abs(step50 - 1.21) < 5e-3, npass, nfail);

%% Chapter 6: ultimatum game, from the code printed in Section 6.6.1
% dims: 1 consequences, 2 rights, 3 fairness, 4 autonomy, 5 privacy/trust,
%       6 social impact, 7 identity, 8 legitimacy, 9 epistemic
S = eye(9); S(1,1) = 25; for d = 2:9, S(d,d) = 0.25; end
S(1,3) = 0.5; S(3,1) = 0.5; S(2,8) = 0.15; S(8,2) = 0.15;
S(7,6) = 0.1; S(6,7) = 0.1; S(5,9) = 0.1; S(9,5) = 0.1;
P = inv(S + 1e-10*eye(9));
stake = 10;
start = [stake 1 0.5 1 0.5 0 0.5 0.5 0.5]';
pcts = [0 10 20 30 40 50]; w = zeros(size(pcts)); pen = w; dist = w;
for i = 1:numel(pcts)
    p = pcts(i);
    v = start; v(1) = stake - stake*p/100;
    v(3) = 0.1 + 0.8*(p/50); v(7) = 0.3 + 0.5*(p/50); v(6) = -0.2 + 0.6*(p/50);
    dl = v - start;
    dist(i) = sqrt(dl' * P * dl);
    if dl(1) > 0 && dl(3) < -0.3, pen(i) = 5; end      % exploitation rule as printed
    w(i) = dist(i) + pen(i);
    fprintf('offer %2d%%: distance %.4f  penalty %.1f  weight %.4f\n', p, dist(i), pen(i), w(i));
end
[~, ibest] = min(w);
fprintf('least-cost offer as printed: %d%%\n', pcts(ibest));
[npass, nfail] = reportb('ch6: exploitation penalty fires on no offer (money never rises)', all(pen == 0), npass, nfail);
[npass, nfail] = reportb('ch6: least-cost offer under the printed code is 20%', pcts(ibest) == 20, npass, nfail);
% the same with the penalty forced onto the 0% offer, as the prose assumes
w2 = dist; w2(1) = w2(1) + 5; [~, i2] = min(w2);
fprintf('least-cost offer with +5 on the 0%% offer: %d%%\n', pcts(i2));
[npass, nfail] = reportb('ch6: still 20% if the 0% offer is penalised by 5', pcts(i2) == 20, npass, nfail);

%% Chapter 9: omega = (1/2) d'Hd with d ~ N(0, s^2 I), symmetric H (n = 2)
syms h11 h12 h22 real
syms s positive
syms x y real
H = [h11 h12; h12 h22];
om = (1/2) * [x y] * H * [x; y];
pdf = exp(-(x^2 + y^2)/(2*s^2)) / (2*sym(pi)*s^2);
E1 = simplify(int(int(om   * pdf, x, -inf, inf), y, -inf, inf));
E2 = simplify(int(int(om^2 * pdf, x, -inf, inf), y, -inf, inf));
[npass, nfail] = report('ch9: E[omega] = (s^2/2) tr(H)', E1 - (s^2/2)*trace(H), npass, nfail);
[npass, nfail] = report('ch9: E[omega^2] = (s^4/4)(tr(H)^2 + 2 tr(H^2))', ...
    E2 - (s^4/4)*(trace(H)^2 + 2*trace(H*H)), npass, nfail);
[npass, nfail] = reportb('ch9: E[omega^2] is NOT (s^2/2) tr(H)', ...
    ~isAlways(simplify(E2 - (s^2/2)*trace(H)) == 0, 'Unknown', 'false'), npass, nfail);

%% Chapter 10: graduated omega = 0.5 + 0.5 * mismatch / total
wts = [1.0 0.7 0.4 0.2];                 % rhythm, tempo, rubato, ornamentation
om_orn = 0.5 + 0.5*wts(4)/sum(wts); om_rhy = 0.5 + 0.5*wts(1)/sum(wts);
fprintf('omega ornamentation %.4f, rhythm alone %.4f\n', om_orn, om_rhy);
[npass, nfail] = reportb('ch10: ornamentation change gives 0.54', abs(om_orn - 0.54) < 5e-3, npass, nfail);
[npass, nfail] = reportb('ch10: rhythm change alone gives 0.72, not 0.93', abs(om_rhy - 0.72) < 5e-3, npass, nfail);

%% Chapter 13: D4 table with r = quarter turn, s = flip across the vertical axis
r = [0 -1; 1 0]; sm = [-1 0; 0 1];
[npass, nfail] = reportb('ch13: s r s = r^-1', isequal(sm*r*sm, inv(r)), npass, nfail);
[npass, nfail] = reportb('ch13: s r   = transpose matrix [0 1; 1 0]', isequal(sm*r, [0 1; 1 0]), npass, nfail);
[npass, nfail] = reportb('ch13: s r^2 = flip across the horizontal axis [1 0; 0 -1]', isequal(sm*r^2, [1 0; 0 -1]), npass, nfail);
[npass, nfail] = reportb('ch13: s r^3 = anti-transpose [0 -1; -1 0]', isequal(sm*r^3, [0 -1; -1 0]), npass, nfail);
% fixed 10-colour grids, by counting cell orbits of each element directly
for n = [3 4 5]
    idx = reshape(1:n^2, n, n);
    c_r   = orbits(idx, rot90(idx));
    c_r2  = orbits(idx, rot90(idx, 2));
    c_ax  = orbits(idx, fliplr(idx));
    c_dg  = orbits(idx, idx');
    ok = (c_r2 == ceil(n^2/2)) && (c_ax == n*ceil(n/2)) && (c_dg == (n^2 + n)/2);
    if mod(n, 2) == 0, ok = ok && (c_r == n^2/4); else, ok = ok && (c_r == (n^2 - 1)/4 + 1); end
    [npass, nfail] = reportb(sprintf('ch13: fixed-cell orbit counts, n = %d (r %d, r2 %d, axis %d, diag %d)', ...
        n, c_r, c_r2, c_ax, c_dg), ok, npass, nfail);
end
% 3x3: Burnside count, and an upper bound on grids with a nontrivial stabiliser
classes3 = (10^9 + 2*10^3 + 10^5 + 2*10^6 + 2*10^6) / 8;
upper3 = 10^5 + 4*10^6;                  % every such grid is fixed by r^2 or by a reflection
fprintf('3x3: %d classes; at most %.2f%% of grids have a nontrivial stabiliser\n', classes3, 100*upper3/10^9);
[npass, nfail] = reportb('ch13: 3x3 class count is an integer', classes3 == floor(classes3), npass, nfail);
[npass, nfail] = reportb('ch13: under 0.5% of 3x3 grids have a nontrivial stabiliser', upper3/10^9 < 0.005, npass, nfail);

%% Chapter 19: the MRI formula, recomputed from the recorded perturbation
%% deviations of the campaign record when it is present next to this script
if isfile('ch19_campaign.json')
    R = jsondecode(fileread('ch19_campaign.json'));
    for arm = {'A', 'B'}
        if isfield(R, arm{1})
            M = R.(arm{1}).mri;
            om = M.omegas(:);
            mri_re = 0.5*mean(om) + 0.3*prctile_lin(om, 75) + 0.2*prctile_lin(om, 95);
            fprintf('ch19 arm %s: recorded MRI %.6f, recomputed %.6f\n', arm{1}, M.mri, mri_re);
            [npass, nfail] = reportb(sprintf('ch19 arm %s: MRI recomputes from its deviations', arm{1}), ...
                abs(mri_re - M.mri) < 1e-9, npass, nfail);
        end
    end
end

%% Appendix C, Theorem C.1(iii): a kernel vector with no zero entry exists
%% exactly when w has at least two nonzero entries
syms a b real
u = null([a b 0]);                        % kernel of w = (a, b, 0), generic a, b
[npass, nfail] = reportb('C.1: kernel of (a,b,0) has dimension 2', size(u, 2) == 2, npass, nfail);
v = [b; -a; 1];                           % in the kernel, no zero entry when a, b ~= 0
[npass, nfail] = report('C.1: (b,-a,1) is in the kernel of (a,b,0)', [a b 0]*v, npass, nfail);
k1 = null(sym([1 0 0]));                  % w = e_1
[npass, nfail] = reportb('C.1: every kernel vector of e_1 has first entry 0', all(k1(1,:) == 0), npass, nfail);

%% Chapter 3: Einstein midpoint
syms c t positive
assumeAlso(c*t^2 < 1);                   % the point lies in the ball
lamx = 2/(1 - c*t^2);                    % conformal factor at radius t (|x| = t)
kx = 2*t/(1 + c*t^2);                    % Klein image of the Poincare radius t
[npass, nfail] = report('ch3: k = lambda x / (lambda - 1)', kx - lamx*t/(lamx - 1), npass, nfail);
[npass, nfail] = report('ch3: gamma(k) = lambda - 1', ...
    1/sqrt(1 - c*kx^2) - (lamx - 1), npass, nfail);
% Klein -> Poincare is (1/2) (x)_c: tanh(artanh(s)/2) = s/(1 + sqrt(1 - s^2)), s = sqrt(c)|k|
syms s positive
[npass, nfail] = reportb('ch3: tanh(artanh(s)/2) = s/(1+sqrt(1-s^2)) on (0,1)', ...
    max(abs(double(subs(tanh(atanh(s)/2) - s/(1 + sqrt(1 - s^2)), s, linspace(0.01, 0.99, 50))))) < 1e-12, ...
    npass, nfail);
% two-point test in the unit ball: x1 = (0.9, 0), x2 = 0
em =einmid([0.9 0; 0 0], [1 1], 1);
naive = (1/(1 - 0.81))*0.9 / (1/(1 - 0.81) + 1);
fprintf('ch3: Einstein midpoint %.4f, naive gamma-weighted %.4f, geodesic midpoint %.4f\n', ...
    em(1), naive, tanh(atanh(0.9)/2));
[npass, nfail] = reportb('ch3: Einstein midpoint of (0.9,0) and 0 is at radius 0.627', abs(em(1) - 0.627) < 5e-4, npass, nfail);
[npass, nfail] = reportb('ch3: naive formula gives 0.756', abs(naive - 0.756) < 5e-4, npass, nfail);
% random pairs, two curvatures: equal hyperbolic distance to both endpoints
rng(3); worst = 0;
for cc = [0.5 1 2]
    for it = 1:200
        u = randn(1, 3); u = u/norm(u)*rand*0.95/sqrt(cc);
        v = randn(1, 3); v = v/norm(v)*rand*0.95/sqrt(cc);
        m = einmid([u; v], [1 1], cc);
        du = 2/sqrt(cc)*atanh(sqrt(cc)*norm(mobaddc(-m, u, cc)));
        dv = 2/sqrt(cc)*atanh(sqrt(cc)*norm(mobaddc(-m, v, cc)));
        duv = 2/sqrt(cc)*atanh(sqrt(cc)*norm(mobaddc(-u, v, cc)));
        worst = max([worst, abs(du - dv), abs(du + dv - duv)]);
    end
end
fprintf('ch3: worst midpoint error over 600 random pairs: %.2e\n', worst);
[npass, nfail] = reportb('ch3: two-point Einstein midpoint is the geodesic midpoint (c = 0.5, 1, 2)', worst < 1e-9, npass, nfail);
% closure: random clouds stay in the ball
inball = true;
for it = 1:200
    X = randn(5, 4); X = X ./ vecnorm(X, 2, 2) .* (rand(5, 1)*0.99);
    m = einmid(X, rand(1, 5), 1); inball = inball && norm(m) < 1;
end
[npass, nfail] = reportb('ch3: midpoint of 200 random weighted clouds lies in the ball', inball, npass, nfail);

%% Appendix C, Proposition C.3.1: the Mobius norm formula and the regrouping
syms x1 x2 y1 y2 real
syms cc positive
xv = [x1 x2]; yv = [y1 y2];
dl = mobaddc(-xv, yv, cc);
A = 1 - 2*cc*dot(xv, yv) + cc^2*dot(xv, xv)*dot(yv, yv);
[npass, nfail] = report('C.3.1: |(-x)+y|^2 (1 - 2c<x,y> + c^2|x|^2|y|^2) = |x-y|^2', ...
    simplify(dot(dl, dl)*A - dot(xv - yv, xv - yv)), npass, nfail);
[npass, nfail] = report('C.3.1: regrouping of the denominator', ...
    A - ((1 - cc*dot(xv, xv))*(1 - cc*dot(yv, yv)) + cc*dot(xv - yv, xv - yv)), npass, nfail);
syms tt positive
[npass, nfail] = reportb('C.3.1: 2 artanh(sqrt(t/(1+t))) = arccosh(1+2t) for t in (0, 50]', ...
    max(abs(double(subs(2*atanh(sqrt(tt/(1+tt))) - acosh(1 + 2*tt), tt, linspace(0.001, 50, 200))))) < 1e-10, ...
    npass, nfail);

%% Chapter 18: hypervolume of a (dims, MAE) frontier, both minimized.
%% The corrected sweep against an independent column-by-column count, and
%% the version previously printed, on random point sets.
rng(18); worst = 0; oldwrong = 0;
for it = 1:500
    k = randi(6); d = randi(9, 1, k); m = 10*rand(1, k);
    hv = hv_sweep(d, m, 10, 10);
    ex = 0;                                           % exact: dims are integers
    for col = 0:9
        sel = m(d <= col);
        if ~isempty(sel), ex = ex + (10 - min(sel)); end
    end
    worst = max(worst, abs(hv - ex));
    oldwrong = oldwrong + (abs(hv_old(d, m, 10, 10) - ex) > 1e-9);
end
fprintf('ch18: hypervolume worst error %.2e over 500 sets; previous version wrong on %d of 500\n', worst, oldwrong);
[npass, nfail] = reportb('ch18: corrected hypervolume equals the exact area', worst < 1e-9, npass, nfail);
[npass, nfail] = reportb('ch18: previously printed hypervolume is wrong on most sets', oldwrong > 250, npass, nfail);

%% Chapter 19: Hanley-McNeil standard error of an AUC near 0.55 with 36
%% positive and 264 negative test cases, and the AUC range in units of it
A = 0.55; n1 = 36; n2 = 264;
Q1 = A/(2 - A); Q2 = 2*A^2/(1 + A);
se = sqrt((A*(1 - A) + (n1 - 1)*(Q1 - A^2) + (n2 - 1)*(Q2 - A^2))/(n1*n2));
fprintf('ch19: AUC standard error %.4f; 43.07%% is %.2f SE below chance, 58.51%% is %.2f SE above\n', ...
    se, (0.5 - 0.4307)/se, (0.5851 - 0.5)/se);
[npass, nfail] = reportb('ch19: AUC standard error rounds to 0.05', abs(se - 0.05) < 0.005, npass, nfail);
[npass, nfail] = reportb('ch19: AUC range lies within two standard errors of 0.5', ...
    max(abs([0.4307 0.5851] - 0.5))/se < 2, npass, nfail);
[npass, nfail] = reportb('ch19: MAE floor with zero precision, recall and F1 is 40.4', ...
    abs((70 + 65 + 67)/5 - 40.4) < 1e-12, npass, nfail);

%% Chapter 12: interaction identities for a second-order model, n = 4
a4 = sym('a', [1 4]); r = sym('r', [4 4]);
r = triu(r, 1); r = r + r.';             % symmetric, zero diagonal
g = @(S) sum(a4(S)) - sum(sum(r(S, S)))/2;
F = 1:4; f = @(S) -g(S);                 % MAE = constant - value; constant dropped
Delta = @(j) f(setdiff(F, j)) - f(F);
Phi = @(i, j) (f(setdiff(F, [i j])) - f(F)) - Delta(i) - Delta(j);
[npass, nfail] = report('ch12: Phi_ij = r_ij (positive = overlap)', Phi(1, 2) - r(1, 2), npass, nfail);
G = @(j, S) f(S) - f(union(S, j));
S = [2]; j = 1;
[npass, nfail] = report('ch12: G_j(S) - G_j(empty) = -sum_{k in S} Phi_jk', ...
    (G(j, S) - G(j, [])) + Phi(1, 2), npass, nfail);
[npass, nfail] = report('ch12: G_j(S) - Delta_j = sum_{k not in S, k ~= j} Phi_jk', ...
    (G(j, S) - Delta(j)) - (Phi(1, 3) + Phi(1, 4)), npass, nfail);
% the two canonical pairs
gv = @(g1, g2, g12) g1 + g2 - 0 - g12;
[npass, nfail] = reportb('ch12: two copies of one signal give Phi = +1', gv(1, 1, 1) == 1, npass, nfail);
[npass, nfail] = reportb('ch12: two halves of an exclusive-or give Phi = -1', gv(0, 0, 1) == -1, npass, nfail);

%% Chapter 7: loss aversion from the printed code, and its dependence on the
%% hand-set secondary coefficients (scaled by s)
ref = [10 1 0.5 1 0 0 0.5 0 0]';
lamfun = @(sc, M) losslam(P, ref, sc, M);
l1 = lamfun(1, 1); l1b = lamfun(1, 7.5);
fprintf('ch7: lambda at the printed coefficients: %.4f (magnitude 1), %.4f (magnitude 7.5)\n', l1, l1b);
for sc = [0 0.25 0.5 1 2]
    fprintf('ch7: secondary loss coefficients x %.2f -> lambda %.4f\n', sc, lamfun(sc, 1));
end
[npass, nfail] = reportb('ch7: lambda at printed coefficients rounds to 2.22', abs(l1 - 2.22) < 5e-3, npass, nfail);
[npass, nfail] = reportb('ch7: lambda does not depend on the magnitude', abs(l1 - l1b) < 1e-12, npass, nfail);
[npass, nfail] = reportb('ch7: with no secondary loss displacement lambda is below 1.1', lamfun(0, 1) < 1.1, npass, nfail);

fprintf('TALLY: %d PASS, %d FAIL\n', npass, nfail);

function a = hv_sweep(d, m, rd, rm)
    % pareto_hypervolume of Section 18.6, as corrected
    keep = d < rd & m < rm; d = d(keep); m = m(keep);
    [d, o] = sort(d); m = m(o); a = 0; best = rm;
    for i = 1:numel(d)
        if i < numel(d), nd = d(i + 1); else, nd = rd; end
        best = min(best, m(i)); a = a + (nd - d(i))*(rm - best);
    end
end

function a = hv_old(d, m, rd, rm)
    % pareto_hypervolume as previously printed
    pts = sortrows([d(:) m(:)]); a = 0; prev = 0;
    for i = 1:size(pts, 1)
        if pts(i, 2) < rm, a = a + (pts(i, 1) - prev)*(rm - pts(i, 2)); prev = pts(i, 1); end
    end
    if prev < rd && pts(end, 2) < rm, a = a + (rd - prev)*(rm - pts(end, 2)); end
end

function q = prctile_lin(x, p)
    % numpy's default percentile (linear interpolation between order statistics)
    x = sort(x(:)); n = numel(x); h = (n - 1)*p/100;
    lo = floor(h); q = x(lo + 1) + (h - lo)*(x(min(lo + 2, n)) - x(lo + 1));
end

function m = einmid(X, w, c)
    % Einstein midpoint in Poincare coordinates, as printed in Section 3.6.1
    lam = 2 ./ (1 - c*sum(X.^2, 2));
    y = sum((w(:).*lam).*X, 1) / sum(w(:).*(lam - 1));
    ny = norm(y);
    if ny == 0, m = y; return; end
    m = tanh(0.5*atanh(sqrt(c)*ny)) * y / (sqrt(c)*ny);
end

function z = mobadd(x, y)
    z = mobaddc(x, y, 1);
end

function z = mobaddc(x, y, c)
    xy = dot(x, y); x2 = dot(x, x); y2 = dot(y, y);
    z = ((1 + 2*c*xy + c*y2)*x + (1 - c*x2)*y) / (1 + 2*c*xy + c^2*x2*y2);
end

function l = losslam(P, ref, sc, M)
    % compute_loss_aversion of Section 7.7.1; dims 1..9 as in Section 6.3
    gain = ref; gain(1) = gain(1) + M; gain(6) = gain(6) + 0.05*M;
    loss = ref; loss(1) = loss(1) - M;
    loss(2) = loss(2) - sc*0.15*M; loss(3) = loss(3) - sc*0.1*M;
    loss(6) = loss(6) - sc*0.1*M;  loss(7) = loss(7) - sc*0.1*M;
    dg = sqrt((gain - ref)'*P*(gain - ref)); dl = sqrt((loss - ref)'*P*(loss - ref));
    l = dl/dg;
end

function c = orbits(idx, img)
    % number of orbits of the involution or rotation sending cell idx(k) to img(k)
    n2 = numel(idx); seen = false(1, n2); c = 0; map = zeros(1, n2);
    map(idx(:)) = img(:);
    for k = 1:n2
        if ~seen(k)
            c = c + 1; j = k;
            while ~seen(j), seen(j) = true; j = map(j); end
        end
    end
end

function [np, nf] = report(name, expr, np, nf)
    ok = all(isAlways(simplify(expr) == 0, 'Unknown', 'false'), 'all');
    [np, nf] = reportb(name, ok, np, nf);
end

function [np, nf] = reportb(name, ok, np, nf)
    if ok
        fprintf('PASS  %s\n', name); np = np + 1;
    else
        fprintf('FAIL  %s\n', name); nf = nf + 1;
    end
end
