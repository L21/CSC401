function AM = align_ibm1(trainDir, numSentences, maxIter, fn_AM)
%
%  align_ibm1
% 
%  This function implements the training of the IBM-1 word alignment algorithm. 
%  We assume that we are implementing P(foreign|english)
%
%  INPUTS:
%
%       dataDir      : (directory name) The top-level directory containing 
%                                       data from which to train or decode
%                                       e.g., '/u/cs401/A2_SMT/data/Toy/'
%       numSentences : (integer) The maximum number of training sentences to
%                                consider. 
%       maxIter      : (integer) The maximum number of iterations of the EM 
%                                algorithm.
%       fn_AM        : (filename) the location to save the alignment model,
%                                 once trained.
%
%  OUTPUT:
%       AM           : (variable) a specialized alignment model structure
%
%
%  The file fn_AM must contain the data structure called 'AM', which is a 
%  structure of structures where AM.(english_word).(foreign_word) is the
%  computed expectation that foreign_word is produced by english_word
%
%       e.g., LM.house.maison = 0.5       % TODO
% 
% Template (c) 2011 Jackie C.K. Cheung and Frank Rudzicz
  
  global CSC401_A2_DEFNS
  
  AM = struct();
  
  % Read in the training data
  [eng, fre] = read_hansard(trainDir, numSentences);

  % Initialize AM uniformly 
  AM = initialize(eng, fre);
  % Iterate between E and M steps
  for iter=1:maxIter,
    AM = em_step(AM, eng, fre);
  end
  % force SENTSTART and SENTEND to be 1
  AM.('SENTSTART').('SENTSTART') = 1;
  AM.('SENTEND').('SENTEND') = 1;
  % Save the alignment model
  save( fn_AM, 'AM', '-mat'); 

  end





% --------------------------------------------------------------------------------
% 
%  Support functions
%
% --------------------------------------------------------------------------------

function [eng, fre] = read_hansard(mydir, numSentences)
%
% Read 'numSentences' parallel sentences from texts in the 'dir' directory.
%
% Important: Be sure to preprocess those texts!
%
% Remember that the i^th line in fubar.e corresponds to the i^th line in fubar.f
% You can decide what form variables 'eng' and 'fre' take, although it may be easiest
% if both 'eng' and 'fre' are cell-arrays of cell-arrays, where the i^th element of 
% 'eng', for example, is a cell-array of words that you can produce with
%
%         eng{i} = strsplit(' ', preprocess(english_sentence, 'e'));
%
  %eng = {};
  %fre = {};

  % TODO: your code goes here.
  
  eng = {numSentences};
  fre = {numSentences};
  e_files = dir([mydir, filesep, '*', '.e']);
  f_files = dir([mydir, filesep, '*', '.f']);
  line_num = 1;
  for file_index=1:length(e_files)
    e_file = fopen([mydir, filesep, e_files(file_index).name]);
    f_file = fopen([mydir, filesep, f_files(file_index).name]);
    e_lines = textscan(e_file, '%s','delimiter','\n');
    f_lines = textscan(f_file, '%s','delimiter','\n');
    for i=1:length(e_lines{1})
        eng{line_num} = strsplit(' ', preprocess(e_lines{1}{i}, 'e'));
        fre{line_num} = strsplit(' ', preprocess(f_lines{1}{i}, 'f'));
        line_num = line_num + 1;
        if line_num > numSentences
            fclose(e_file);
            fclose(f_file);
            return
        end
    end
    fclose(e_file);
    fclose(f_file);
  end
end

function AM = initialize(eng, fre)
%
% Initialize alignment model uniformly.
% Only set non-zero probabilities where word pairs appear in corresponding sentences.
%
    % AM.(english_word).(foreign_word)
    words = {};
    AM = {};
    % TODO: your code goes here
    % for each sentence in english
    for sentence_num=1:numel(eng)
        eng_sentence = eng{sentence_num};
        fre_sentence = fre{sentence_num};       
        %remove SENTEND
        if strcmp(fre_sentence{numel(fre_sentence)}, 'SENTEND')
            fre_sentence(numel(fre_sentence)) = [];
        end
        %remove SENTSTART
        if strcmp(fre_sentence{1}, 'SENTSTART')
            fre_sentence(1) = [];
        end
        % for each word in that sentence
        % except for SENTSTART and SENTEND
        for word=2:numel(eng_sentence)-1
            % if the word has appeared before
            if isfield(words, (eng_sentence{word}))
                % add new corresponding french sentence's words to the list
                % of alignments
                words.(eng_sentence{word}).fre = union(words.(eng_sentence{word}).fre, (fre_sentence));
            % if the word is new
            else
                % add corresponding french sentence's words to the list of
                % alignments
                words.(eng_sentence{word}).fre = (fre_sentence);
            end
        end
    end
    eng_words = fieldnames(words);
    % for each english word in words
    for i = 1:numel(eng_words)
        % calculate inital prob. of alignment by dividing all corresponding
        % french words
        probab = 1/length(words.(eng_words{i}).fre);
        % get all french words corresponds to a english word
        fre_words = words.(eng_words{i}).fre;
        % for each french word
        for j = 1:numel(fre_words)
            % assign inital probab to it
            AM.(eng_words{i}).(fre_words{j}) = probab;
        end
    end
end

function t = em_step(t, eng, fre)
% 
% One step in the EM algorithm.
%
  % TODO: your code goes here
  % set tcount(f, e) to 0 for all f,e
  tcount = {}; 
  % set total(e) to 0 for all e
  total = {};
  % for each sentence pair (F, E) in training corpus
  for s_index=1:numel(eng)      
      F = fre{s_index};          
      E = eng{s_index};
      if strcmp(E{numel(E)}, 'SENTEND')
          E(numel(E)) = [];
      end
      %remove SENTSTART
      if strcmp(E{1}, 'SENTSTART')
          E(1) = [];
      end
      if strcmp(F{numel(F)}, 'SENTEND')
          F(numel(F)) = [];
      end
      %remove SENTSTART
      if strcmp(F{1}, 'SENTSTART')
          F(1) = [];
      end
      F_uniq_words = unique(F);          
      E_uniq_words = unique(E);
      % for each unique word f in F
      for fw_index=1:numel(F_uniq_words)
          % denom_c = 0
          denom_c = 0;
          f = (F_uniq_words{fw_index});
          f_count = sum(strcmp(F,f));
          % for each unique word e in E
          for ew_index=1:numel(E_uniq_words)
              % denom_c += P(f|e) * F.count(f)
              e = (E_uniq_words{ew_index});
              denom_c = denom_c ...
                        + t.(e).(f)...
                        * f_count;
          end
          % for each unique word e in E
          for ew_index=1:numel(E_uniq_words)
              e = (E_uniq_words{ew_index});
              e_count = sum(strcmp(E,e));
              % tcount(f, e) += 
              % P(f|e) * F.count(f) * E.count(e) / denom_c
              if isfield(tcount, (f))
                  if ~isfield(tcount.(f), (e))
                      tcount.(f).(e) = 0;
                  end
              else
                  tcount.(f) = struct();
                  tcount.(f).(e) = 0;
              end
              to_add = t.(e).(f) * f_count...
                       * e_count / denom_c;
              tcount.(f).(e) = tcount.(f).(e) + to_add;   
              %  total(e) += P(f|e) * F.count(f) * E.count(e) / denom_c
              if ~isfield(total, (e))
                  total.(e) = 0;
              end
              total.(e) = total.(e) + to_add;
          end
      end
  end
  % for each e in domain(total(:))
  e_list = fieldnames(total);
  for i=1:numel(e_list)
      e = e_list{i};
      % for each f in domain(tcount(:,e))
      f_list = fieldnames(tcount);
      for j=1:numel(f_list)
          f = f_list{j};
          if isfield(tcount.(f), (e))
              % P(f|e) = tcount(f, e) / total(e)
              t.(e).(f) = tcount.(f).(e) / total.(e);
          end
      end
  end
end

