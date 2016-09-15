function [gmm, L] = computeLikelihood(x, gmm)
    % number of training cases
    N = size(x, 1);
    % number of dimensions
    D = size(x, 2);
    % number of gaussians
    M = size(gmm.weights, 2);
    for m=1:M
        % 1/cov as a 1xD vector
        covVector = 1./diag(gmm.cov(:,:,m))';
        % log(b_m(X))
        logbGivenX(:,m) = -0.5 * sum((x - ones(N,1) * gmm.means(:,m)').^2 ...
            .* (ones(N, 1) * covVector),2)... % numerator
            - (D/2 * log(2 * pi)) ... % denominator
            - 0.5 * sum(log(1./covVector));
    end
    %mx = max(logbGivenX');
    %bGivenX = exp(logbGivenX-(ones(M,1)*mx)');
    bGivenX = exp(logbGivenX);
    % p(m|X)
    for m=1:M
        const(:,m) = gmm.weights(m) * bGivenX(:,m);        
    end
    denominator = sum(const, 2);
    for m=1:M
        PmGivenX(:,m) = const(:,m)./denominator;
    end
    % normalize log likelihood by dividing number of inputs from this
    % speaker
    L = sum(sum(PmGivenX.*(log(ones(N,1)*gmm.weights) + logbGivenX))) / N;
end