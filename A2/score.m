function Bleu = score(candicate, reference, n)
    
    %candicate = strsplit(' ', candicate);
    candicate_length = length(candicate);
    
    
    reference_length = length(reference);
    sub_reference_length = {};
    for i = 1:reference_length
        length_r = length(strsplit(' ', reference{i}));
        sub_reference_length{i} = length_r;
    end
    
    r = sub_reference_length{1};
    for i = 1:reference_length
        if abs(sub_reference_length{i} - candicate_length) < abs(r - candicate_length)
            r = sub_reference_length{i};
        end
    end
    brevity = r/candicate_length;
    BP = 0;
    if brevity < 1
        BP = 1;
    else
        BP = exp(1- brevity);
    end
    
    pn = 1;    
    
    for index = 1:n
        number = 0;
        for k = index:candicate_length
            if index == 1
                string = [' ', candicate{k},' '];
            elseif index == 2
                string = [' ', candicate{k-1},' ',candicate{k},' '];
            elseif index == 3
                string = [' ', candicate{k-2},' ', candicate{k-1},' ',candicate{k},' '];
            end
            for w = 1:reference_length 
                if (strfind([' ',reference{w},' '], string))
                    number  = number + 1;
                    break;
                end
            end
        end
        
        pn = pn * number / (candicate_length + 1 - index);
        
        
    end
    Bleu = BP * power(pn,1/n);

return;
    
