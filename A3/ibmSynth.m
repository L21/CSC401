%lik_dir = 'done/part2';
annotation_dir = '/u/cs401/speechdata/Testing';
%annotation_dir = 'testing';
files = dir([annotation_dir, filesep, 'unkn_*.txt']);
% output dir for generated audio
flac_dir = './ibm_flac';
mkdir(flac_dir);
% outout dir for re-generated text
ibm_flac_text_dir = 'ibm_flac_text';

for i=1:length(files)
    % get reference text
    ref_text = textread([annotation_dir, filesep...
           , 'unkn_', num2str(i), '.txt'], '%s', 'delimiter','\n')';
    % remove time stamps 
    ref_text = regexprep(ref_text{1}, '[0-9]+ ', '');
    
    % get most likely speaker
    lik = textread([lik_dir, filesep, 'unkn_', num2str(i), '.lik'], '%s', 'delimiter','\n');
    lik = lik{1};
    if regexp(lik,'name\: F')
        voice = 'en-US_LisaVoice';
    else
        voice = 'en-US_MichaelVoice';
    end
    
    % set flac filename
    filename = [flac_dir, filesep, 'unkn_', num2str(i), '.flac'];
    % get flac file
    [status, r] = unix(['curl',...
    ' -u "d80d4fac-f681-4663-8eee-5e863bd99697":"WSLyVfyol1HO"',...
    ' -X POST -H "content-type: application/json" ',...
    ' -H "accept: audio/flac"',...
    ' -d "{\"text\":\" ',ref_text,' \"}"',...
    ' "https://stream.watsonplatform.net/text-to-speech/api/v1/synthesize?',...
    'voice=', voice, '" >', filename]);
    if status ~= 0
        fprintf('something is wrong.....\n');
    end
end
% get text file
processSpeechToText(flac_dir, ibm_flac_text_dir);

[SE, IE, DE, LEV_DIST] =Levenshtein([ibm_flac_text_dir, filesep, 'hypo.txt'], annotation_dir);
