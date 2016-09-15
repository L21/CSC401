function logProb = lm_prob(sentence, LM, type, delta, vocabSize)
%
%  lm_prob
% 
%  This function computes the LOG probability of a sentence, given a 
%  language model and whether or not to apply add-delta smoothing
%
%  INPUTS:
%
%       sentence  : (string) The sentence whose probability we wish
%                            to compute
%       LM        : (variable) the LM structure (not the filename)
%       type      : (string) either '' (default) or 'smooth' for add-delta smoothing
%       delta     : (float) smoothing parameter where 0<delta<=1 
%       vocabSize : (integer) the number of words in the vocabulary
%
% Template (c) 2011 Frank Rudzicz

  logProb = -Inf;

  % some rudimentary parameter checking
  if (nargin < 2)
    disp( 'lm_prob takes at least 2 parameters');
    return;
  elseif nargin == 2
    type = '';
    delta = 0;
    vocabSize = length(fieldnames(LM.uni));
  end
  if (isempty(type))
    delta = 0;
    vocabSize = length(fieldnames(LM.uni));
  elseif strcmp(type, 'smooth')
    if (nargin < 5)  
      disp( 'lm_prob: if you specify smoothing, you need all 5 parameters');
      return;
    end
    if (delta <= 0) or (delta > 1.0)
      disp( 'lm_prob: you must specify 0 < delta <= 1.0');
      return;
    end
  else
    disp( 'type must be either '''' or ''smooth''' );
    return;
  end

  words = strsplit(' ', sentence);
  word_length = length(words);
  prob_of_sentence = 1;
  if delta == 0
      for index = 2 : word_length
          if isfield(LM.bi.(words{index-1}),words{index}) && ...
                  isfield(LM.uni,words{index-1})
              prob_of_sentence = prob_of_sentence * ...
                  LM.bi.(words{index-1}).(words{index}) /...
              LM.uni.(words{index-1});
          else
              prob_of_sentence = 0;
              break
          end
      end
  else
      for index = 2 : word_length
          if isfield(LM.uni,words{index-1})
              if isfield(LM.bi.(words{index-1}), words{index})
                  prob_of_sentence = prob_of_sentence * ...
                      (LM.bi.(words{index-1}).(words{index}) + delta) /... 
                      (LM.uni.(words{index-1}) + delta * vocabSize);
                  
              else
                  prob_of_sentence = prob_of_sentence * ...
                      (0 + delta) / ...
                      (LM.uni.(words{index-1}) + delta * vocabSize);
                  
              end
                  
          else
              prob_of_sentence = prob_of_sentence *  delta / ...
                  (delta *vocabSize);
              
          end
      end
  end
              
             
          
  % TODO: the student implements the following
  % TODO: once upon a time there was a curmudgeonly orangutan named Jub-Jub.
  logProb =log2(prob_of_sentence);
return
