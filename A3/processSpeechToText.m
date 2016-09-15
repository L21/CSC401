function processSpeechToText(test_dir, output_dir)
    files = dir([test_dir, filesep,'unkn_*.flac']);
    mkdir(output_dir);
    hypo_text = fopen([output_dir, filesep, 'hypo.txt'], 'w');
    % for each flac file, 
    for file_index = 1:length(files)
        fprintf(['passing unkn_', num2str(file_index), '.flac to Watson ...\n']);
       [status, r] = unix([...
           'env LD_LIBRARY_PATH=''''',...
           ' curl -u "82324dc9-ee9d-4813-a6b6-81bb038e3f55":"hDT9yNvqS4lq" ',...
           '-X POST --header "Content-Type: audio/flac" ',...
           '--header "Transfer-Encoding: chunked" --data-binary @',test_dir,...
           filesep, 'unkn_', num2str(file_index), '.flac' ,...
           ' "https://stream.watsonplatform.net/speech-to-text/api/v1/recognize?continuous=true"']);
       % sanity check for returned JSON
       if status == 0
           r = mat2str(r);
           % extract transcript from returned JSON
           % find index of "transcript": header
           start_index = strfind(r,'"transcript":');
           start_index = start_index(1) + length('"transcript":');
           end_index = strfind(r,'}');
           end_index = end_index(1) - 1;
           % remove uncesary double qoutes
           r = r(start_index:end_index -1);
           indeces = strfind(r,'"');
           start_index = indeces(1) + 1;
           end_index = indeces(2) - 1;
           r = r(start_index:end_index);
           % fix double single quotes
           r = regexprep(r, '\''\''', '''');
           % get only the filename (without extension)
           output = fopen([output_dir, filesep, 'unkn_', num2str(file_index), '.txt'], 'w');
           fprintf(hypo_text, [r, '\n']);
           fprintf(output, [r, '\n']);
           fclose(output);
       else
           fprintf('ERROR: curl to Watson returned an error...\n');
       end
    end
    fclose(hypo_text);
    fprintf('All done.\n');
end