% parameters for training
clear gmms files;
M = 8;
max_iter = 20;
epsilon = 0.01;
dir_train = '/u/cs401/speechdata/Training';
%dir_train = 'speakers';
% train models
gmms = gmmTrain(dir_train, max_iter, epsilon, M);

% load test file
test_dir = '/u/cs401/speechdata/Testing';
%test_dir = 'testing';
files = dir([test_dir, filesep,'*.mfcc']);
% for each utterance
for file_index = 1:length(files)
    x = dlmread([test_dir, filesep, files(file_index).name]);
    % calculate logP for each speaker's gmm
    for gmm_index = 1:length(gmms)
        [~, L] = computeLikelihood(x, gmms{gmm_index});
        results(gmm_index) = L;
    end
    % create unkn_N.lik
    fid = fopen(['unkn_', num2str(file_index), '.lik'], 'w');
    % find top 5
    [value, index] = sort(results, 'descend');
    for i=1:5
         % save top 5 gmm to unkn_N.lik
        fprintf(fid,'name: %s, log probability: %f\n',gmms{index(i)}.name, results(index(i)));
    end
    fclose(fid);
    fprintf('first choice: name: %s, log confidence: %f\n',gmms{index(1)}.name, results(index(1)));
    log_prob(file_index) = results(index(1));
end
fprintf('average confidence of first choice: %f\n', mean(log_prob));
