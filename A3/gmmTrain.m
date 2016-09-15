
function gmms = gmmTrain(dir_train, max_iter, epsilon, M )
% gmmTain
%
%  inputs:  dir_train  : a string pointing to the high-level
%                        directory containing each speaker directory
%           max_iter   : maximum number of training iterations (integer)
%           epsilon    : minimum improvement for iteration (float)
%           M          : number of Gaussians/mixture (integer)
%
%  output:  gmms       : a 1xN cell array. The i^th element is a structure
%                        with this structure:
%                            gmm.name    : string - the name of the speaker
%                            gmm.weights : 1xM vector of GMM weights
%                            gmm.means   : DxM matrix of means (each column 
%                                          is a vector
%                            gmm.cov     : DxDxM matrix of covariances. 
%                                          (:,:,i) is for i^th mixture
% get directory names of speakers
    speaker_dir_names = strsplit(strtrim(ls(dir_train)));
    % for each speaker
    for speaker_index = 1:length(speaker_dir_names)
        % initalize gmm struct for each speaker
        gmm = struct();
        speaker_dir = speaker_dir_names{speaker_index};
        gmm.name = speaker_dir;
        % get all mfcc files
        files = dir([dir_train, filesep, speaker_dir, filesep,'*.mfcc']);
        % load files into a single input matrix
        x = [];
        for file_index = 1:length(files)
            x = [x; dlmread([dir_train, filesep, speaker_dir,...
                filesep, files(file_index).name])];
        end
        % initialize likelihood, mean and covariance for each Gaussian
        [mus, weights, cov] = initialize(x, M);
        gmm.means = mus;
        gmm.cov = cov;
        gmm.weights = weights;
        gmms{speaker_index} = gmm;
        % starts the training
        prev_L = -Inf;
        improv = Inf;
        
        % begin iteration
        for j = 0:max_iter
            if improv <= epsilon
                break;
            end
            [gmm, L] = computeLikelihood(x, gmm);
            improv = L - prev_L;
            prev_L = L;
            gmms{speaker_index} = gmm;
        end
    end
end

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
    % b_m(X)
    bGivenX = exp(logbGivenX);
    % p(m|X)
    for m=1:M
        const(:,m) = gmm.weights(m) * bGivenX(:,m);        
    end
    denominator = sum(const, 2);
    for m=1:M
        PmGivenX(:,m) = const(:,m)./denominator;
    end
    L = sum(sum(PmGivenX.*(log(ones(N,1)*gmm.weights) + logbGivenX))) / N;
    gmm = updateParameters(gmm, x, PmGivenX);
end

function gmm = updateParameters(gmm, x, PmGivenX)
    % number of training cases
    N = size(x, 1);
    % number of dimensions
    D = size(x, 2);
    % number of gaussians
    M = size(gmm.weights, 2);
    for m=1:M
        % update weights
        const = sum(PmGivenX(:,m));
        gmm.weights(m) = const / N;
        % update weights
        % temp--> used for matrix multiplication
        temp = eye(D);
        temp = temp(1,:);
        mthMean = sum((PmGivenX(:,m) * temp)' * x) / const;
        gmm.means(:,m) = mthMean(1,:);
        % update cov
        % cov as a 1xD vector
        covVector = diag(gmm.cov(:,:,m))';
        mthCov = sum((PmGivenX(:,m) * temp)' * (x.^2)) / const;
        gmm.cov(:,:,m) = diag(mthCov(1,:) - (gmm.means(:,m).^2)');
    end
end

function [mus, weights, cov] = initialize(x, M)
    % random initlaize means from M rows in x
    index = (size(x, 1) - M) * rand(1);
    mus = x(index:(index + M - 1), :)';
    % initalize all weights to 1/M
    weights = 1/M * ones(1,M);
    % initialize convariance matrix to identity 
    cov = repmat(eye(size(x,2)),1,1,M);
end