function [SE, IE, DE, LEV_DIST] =Levenshtein(hypothesis,annotation_dir)
% Input:
%	hypothesis: The path to file containing the the recognition hypotheses
%	annotation_dir: The path to directory containing the annotations
%			(Ex. the Testing dir containing all the *.txt files)
% Outputs:
%	SE: proportion of substitution errors over all the hypotheses
%	IE: proportion of insertion errors over all the hypotheses
%	DE: proportion of deletion errors over all the hypotheses
%	LEV_DIST: proportion of overall error in all hypotheses

    SE = 0;
    IE = 0;
    DE = 0;
    LEV_DIST = 0;
    wc = 0;
    % get hypotheses
    hypo_texts = textread(hypothesis, '%s', 'delimiter','\n');
    wer_indi = fopen('wer_individual_utterances.txt', 'w');
    % for each hypothesis
    for f=1:length(hypo_texts)
        fprintf(wer_indi, ['Utterance: unkn_', num2str(f), '\n']);
        % remove time stamps 
        hypo_text = regexprep(hypo_texts{f}, '[0-9]+ ', '');
        % remove punctuations
        hypo_text = regexprep(hypo_text, '[\.\,\''\?\!\:\;\(\)\"]', '');
        % remove redundunt spaces
        hypo_text = regexprep(hypo_text, ' +', ' ');
        hypo_text = regexprep(hypo_text, ' +$', '');
        fprintf(wer_indi, ['Recognized text:', hypo_text, '\n']);
        hypo_text = strsplit(hypo_text, ' ');
        % get corresponding reference
        ref_text = textread([annotation_dir, filesep...
            , 'unkn_', num2str(f), '.txt'], '%s', 'delimiter','\n')';
        % remove time stamps 
        ref_text = regexprep(ref_text{1}, '[0-9]+ ', '');
        % remove punctuations
        ref_text = regexprep(ref_text, '[\.\,\''\?\!\:\;\(\)\"]', '');
        ref_text = strsplit(ref_text, ' ');

        % allocate matrix R[n+1, m+1]
        n = length(ref_text);
        m = length(hypo_text);
        % update total word count
        wc = wc + n;
        % initialize matrix R
        R = zeros(n + 1, m + 1);
        % initialize backtrace matrix B
        B = cell([n + 1, m + 1]);
        % first row and first column set to Inf
        R(:, 1) = Inf;
        R(1, :) = Inf;
        % R[0,0] = 0
        R(1,1) = 0;
        % for i := 1..n
        for i = 2:n + 1
            % for j := 1..m
            for j = 2:m + 1
                [R(i, j), index] = min([R(i-1, j) + 1,...
                                        R(i-1, j-1), ...
                                        R(i, j-1) + 1]);
                % update backtrace
                options = [[i-1,j]; [i-1, j-1]; [i, j-1]];
                B{i,j} = struct();
                B{i,j}.prev = options(index, :);
            end
            if index == 2 
                if strcmp(ref_text{i - 1}, hypo_text{j - 1}) ~= 1
                    R(i, j) = R(i, j) + 1;
                end
            end
        end
        [~, index] = min(R(:, m + 1));
        SE = SE + sum(diag(R));
        fprintf(wer_indi, ['SE: ', num2str(sum(diag(R))/n), '\n']);
        current = [n, m];
        current_IE = 0;
        current_DE = 0;
        while ~isequal(current, [1 1])
            % get the previous coordinate of the path
            cur_prev = B{current(1), current(2)}.prev;
            % check the row number of prev
            switch cur_prev(1)
                % if prev is on the same row as current, there is an IE
                case current(1)
                    IE = IE + 1;
                    current_IE = current_IE + 1;
                otherwise
                    % otherwise check the column number of prev
                    switch cur_prev(2)
                        % if prev is on the same column as current, there is a DE 
                        case current(2)
                            DE = DE + 1;
                            current_DE = current_DE + 1;
                        otherwise
                            break;
                    end
            end
            % set current to prev
            current = B{cur_prev(1), cur_prev(2)}.prev;
        end
        % record individual error rates
        fprintf(wer_indi, ['DE: ', num2str(current_DE/n), '\n']);
        fprintf(wer_indi, ['IE: ', num2str(current_IE/n), '\n']);
        fprintf(wer_indi, ['LEV_DIST: ', num2str(current_IE/n + ...
        current_DE/n + sum(diag(R))/n), '\n\n']);
    end
    fclose(wer_indi);
    SE = SE/wc;
    IE = IE/wc;
    DE = DE/wc;
    LEV_DIST = SE + IE + DE;
end
