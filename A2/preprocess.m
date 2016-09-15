function outSentence = preprocess( inSentence, language )
%
%  preprocess
%
%  This function preprocesses the input text according to language-specific rules.
%  Specifically, we separate contractions according to the source language, convert
%  all tokens to lower-case, and separate end-of-sentence punctuation 
%
%  INPUTS:
%       inSentence     : (string) the original sentence to be processed 
%                                 (e.g., a line from the Hansard)
%       language       : (string) either 'e' (English) or 'f' (French) 
%                                 according to the language of inSentence
%
%  OUTPUT:
%       outSentence    : (string) the modified sentence
%
%  Template (c) 2011 Frank Rudzicz 

  global CSC401_A2_DEFNS
  
  % first, convert the input sentence to lower-case and add sentence marks 
  inSentence = [CSC401_A2_DEFNS.SENTSTART ' ' lower( inSentence ) ' ' CSC401_A2_DEFNS.SENTEND];

  % trim whitespaces down 
  inSentence = regexprep( inSentence, '\s+', ' '); 

  % initialize outSentence
  outSentence = inSentence;

  % perform language-agnostic changes
  % TODO: your code here
  %    e.g., outSentence = regexprep( outSentence, 'TODO', 'TODO');
  outSentence = regexprep(outSentence,'([\?\!\.\,:;\(\)\[\]/\$\%\&\*\+\-<>="`])',' $1 ');
  switch language
   case 'e'
      % single quote followed by a space or line end
      outSentence = regexprep(outSentence,'(?!s)('') ', ' $1');
      outSentence = regexprep(outSentence,'(?!s)('')$', ' $1');
      
      %separate 's, 'm, 'd, 'o, 've, 'll and 're cases
      outSentence = regexprep(outSentence,'(''([smo]|(re)|(ve)|(ll))) ', ' $1 ');
      %separate n't case
      outSentence = regexprep(outSentence,'(n''t )', ' $1');
      %separate s' case
      outSentence = regexprep(outSentence,'(\ws'' )', ' $1 ');
      %separate single quotes
      outSentence = regexprep(outSentence,'''''', ''' ''');

    % TODO: your code here
   case 'f'
       outSentence = regexprep(outSentence,'(l'')', '$1 ');
       outSentence = regexprep(outSentence,'(\s*\w'')', '$1 ');
       outSentence = regexprep(outSentence,'(qu'')', '$1 ');
       outSentence = regexprep(outSentence,'(''on)', ''' on');
       outSentence = regexprep(outSentence,'(''il)', ''' il');
       outSentence = regexprep(outSentence,'\s*(d'')\s*(abord|accord|ailleurs|habitude)\s*',' d''$2 ');
    % TODO: your code here
  end
  
  outSentence = regexprep(outSentence,'(  +)',' ');
  outSentence = regexprep(outSentence,'( +$)','');
  % change unpleasant characters to codes that can be keys in dictionaries
  outSentence = convertSymbols( outSentence );

