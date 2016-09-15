%
% evalAlign
%
%  This is simply the script (not the function) that you use to perform your evaluations in 
%  Task 5. 

% some of your definitions
trainDir     = '/u/cs401/A2_SMT/data/Hansard/Training/';
testDir      = '/u/cs401/A2_SMT/data/Hansard/Testing/';
fn_LME       = 'lm_e';
fn_LMF       = 'lm_f';
lm_type      = '';
delta        = 0.5;
vocabSize    = 500; 
numSentences = 100;

% Train your language models. This is task 2 which makes use of task 1
if exist(fn_LME, 'file') == 2
  loaded_file = load(fn_LME, '-mat');
  LME = loaded_file.LM;
else
  LME = lm_train( trainDir, 'e', fn_LME );
end
if exist(fn_LMF, 'file') == 2
  loaded_file = load(fn_LMF, '-mat');
  LME = loaded_file.LM;
else
  LMF = lm_train( trainDir, 'f', fn_LMF );
end


% grab reference sentences.
google_e_lines = textread([testDir, filesep, 'Task5.google.e'], '%s','delimiter','\n');
hansard_e_lines = textread([testDir, filesep, 'Task5.e'], '%s','delimiter','\n');
f_lines = textread([testDir, filesep, 'Task5.f'], '%s','delimiter','\n');
references = {};

% Train your alignment model of French, given English
sentences_nums = [1000, 10000, 15000, 30000];
for i=1:length(f_lines)
    % BlueMix translation
    [status, result] = unix(['curl -u "64d73d9b-d91c-437f-a085-d2fbb30294e6":"XQ5oOmmxZdU6" -X POST -F "text=', f_lines{i}, '" -F "source=fr" -F "target=en" "https://gateway.watsonplatform.net/language-translation/api/v2/translate"']);
    if (status == 0)
        watson_result = result;
    else
        return;
    end
    hansard_e_lines{i} = preprocess(hansard_e_lines{i}, 'e');
    % Remove SNETSTART
    hansard_e_lines{i} = strrep(hansard_e_lines{i}, 'SENTSTART', '');
    % Remove SENTEND
    hansard_e_lines{i} = strrep(hansard_e_lines{i}, 'SENTEND', '');
    
    google_e_lines{i} = preprocess(google_e_lines{i}, 'e');
    % Remove SNETSTART
    google_e_lines{i} = strrep(hansard_e_lines{i}, 'SENTSTART', '');
    % Remove SENTEND
    google_e_lines{i} = strrep(hansard_e_lines{i}, 'SENTEND', '');
    
    % Remove SNETSTART
    watson_result = preprocess(watson_result, 'e');
    watson_result = strrep(watson_result, 'SENTSTART', '');
    % Remove SENTEND
    watson_result = strrep(watson_result, 'SENTEND', '');
    sentences = {(hansard_e_lines{i}), (google_e_lines{i}), (watson_result)};
    references{i} = sentences;
    fre{i} = preprocess((f_lines{i}), 'f');
end
% for each of the traning sizes

fid = fopen('result.txt','wt');

file_names = {'1K', '10K', '15K', '30K'};
for i=1:4
    fprintf(fid, ['sample size - ', file_names{i}, '\n']);
    numSentences = sentences_nums(i);
    
    if exist(['ibm', (file_names{i})], 'file') == 2
      Align_model = load(['ibm', (file_names{i})], '-mat');
      AMFE = Align_model.AM;
    else
      AMFE = align_ibm1( trainDir, numSentences, (['ibm', (filenames{i})]));
    end
    % ... TODO: more 

    % TODO: a bit more work to grab the English and French sentences. 
    %       You can probably reuse your previous code for this  

    % 25x1 cells.

    for j=1:length(f_lines)
        % Decode the test sentence 'fre'
        eng{j} = decode(fre{j}, LME, AMFE, 'smooth', delta, vocabSize );
        % Remove SNETSTART
        eng{j} = strrep(eng{j}, 'SENTSTART', '');
        % Remove SENTEND
        eng{j} = strrep(eng{j}, 'SENTEND', '');
        % TODO: perform some analysis
        for n=1:3
            fprintf(fid, 'n = %f: \n', n);
            % requires score.m
            bleu_score = score(eng{j}, references{j}, n);
            fprintf(fid, 'bleu score: %f \n', bleu_score); 
        end
    end
end
fclose(fid);
    
