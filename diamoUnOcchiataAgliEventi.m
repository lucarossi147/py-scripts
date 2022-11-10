clearvars
close all
clc

% caricamento waveform stereotipata calcolata durante un'esecuzione precedente
load wave1

rootFolder = "extracted events";

experimentNames = dir(rootFolder);

sr = 1;
dt = 1/sr;

stereotypeL = 35;

eventStereotype = zeros(1, stereotypeL);
goodEventsTot = 0;

amplitudes = zeros(10000, 1);
d50s = zeros(10000, 1);
SW = zeros(10000, 1);
SF = zeros(10000, 1);

for i = 1:length(experimentNames)
    if experimentNames(i).name(1) == '.'
        continue
    end

    experimentName = string(experimentNames(i).name);
    experimentFolder = experimentName;
    dataFileName = experimentName + ".dat";
    detailsFileName = "details.csv";

    dataPath = fullfile(rootFolder, experimentFolder, dataFileName);
    detailsPath = fullfile(rootFolder, experimentFolder, detailsFileName);

    % caricametno dati con gli eventi
    dataFid = fopen(dataPath, "rb");
    events = fread(dataFid, inf, "float64");
    fclose(dataFid);

    % caricametno dettagli file
    detailsFid = fopen(detailsPath, "r");
    lineCount = 0;
    eventLengths = zeros(1000, 1);
    while true
        tline = fgetl(detailsFid);
        if ~ischar(tline)
            break
        end
        tline = string(tline);
        if tline.strlength > 0
            lineCount = lineCount+1;
            if lineCount > 2
                values = tline.split(",");
                eventLengths(lineCount-2) = values(2).double-values(1).double;
            end
        end
    end
    fclose(detailsFid);

    N = lineCount-2;
    eventLengths(N+1:end) = [];

    % ciclo su tutti gli eventi
    b = 1;
    eventAvg = zeros(1, stereotypeL);
    goodEventsN = 0;
    figure, hold on
    for l = 1:N
        e = b+eventLengths(l)-1;

        event = events(b:e);
        d = e-b+1;
        b = e+1;

        % scarto eventi troppo brevi
        if d < 30
            continue
        end

        % calcolo la baseline sul primo 20% del primo terzo dei dati e
        % sull'ultimo 20% dell'ultimo terzo dei dati
        xBaseline = [1:round(d/3*0.2), round(d-d/3*0.2):d];
        baseline = mean(event(xBaseline));
        amplitude = baseline-min(event);

        % istante in cui l'evento supera il 50% dell'escursione
        b50 = find(event < baseline-amplitude/2, 1, 'first');
        % istante in cui l'evento torna al di sotto del 50% dell'escursione
        e50 = find(event < baseline-amplitude/2, 1, 'last');
        % durata da 50% a 50%
        d50 = e50-b50;

        idx = goodEventsTot+goodEventsN+1;

        % faccio il logaritmo di ampiezze e durate perchè gli istogrammi in
        % scala logaritmica sono più simmetrici

        % inoltre faccio un whitening semplificato: sottraggo la media e
        % divido per la deviazione standard calcolate in un'esecuzione
        % precedente
        SA = (log(amplitude)+21.175012761120229)/0.412530189443423;
        SD = (log(d50)-3.982651178110859)/1.020579064361968;

        SF(idx) = sqrt(SA^2+SD^2);

        % forma d'onda normalizzata:
        % in ampiezza dividendo per amplitude
        % in durata facendo la spline su un numero fisso di campioni
        d = length(event);
        x = 0:d-1;
        xNorm = linspace(0, d-1, stereotypeL*3+4);
        eventNorm = spline(x, event/amplitude, xNorm);
        eventNorm = eventNorm(stereotypeL+3:2*stereotypeL+2);

        SW(idx) = sqrt(sum((eventNorm-eventStereotypeStored).^2));

        % aggiorno solo se SW e SF sono sotto una soglia che decido
%         if SW(idx) < 2 && SF(idx) < 2.5
            amplitudes(idx) = amplitude;
            d50s(idx) = d50;
            eventAvg = eventAvg+eventNorm;
            goodEventsN = goodEventsN+1;
            plot(eventNorm)
%         end
    end
    eventStereotype = eventStereotype+eventAvg;
    goodEventsTot = goodEventsTot+goodEventsN;

    eventAvg = eventAvg/goodEventsN;
end

eventStereotype = eventStereotype/goodEventsTot;
figure, plot(linspace(0, 1, stereotypeL), eventStereotype, 'r', 'LineWidth', 3)
% figure, plot(events)
amplitudes(goodEventsTot+1:end) = [];
d50s(goodEventsTot+1:end) = [];
figure, loglog(amplitudes, d50s, '.')

[histA, xA] = hist(log(amplitudes), 30);
figure, semilogx(exp(xA), histA)
[histD, xD] = hist(log(d50s), 30);
figure, semilogy(histD, exp(xD))

% printo media e deviazione standard dei logaritmi da utilizzare in
% esecuzioni successive
format long
logA = log(amplitudes);
disp([mean(logA), std(logA)])
logANorm = (logA-mean(logA))/std(logA);
logD = log(d50s);
disp([mean(logD), std(logD)])
logDNorm = (logD-mean(logD))/std(logD);


SW(goodEventsTot+1:end) = [];
SF(goodEventsTot+1:end) = [];

figure, hist(SW, 30)
figure, hist(SF, 30)

% salvo waveform stereotipata da utilizzare durante esecuzioni successive
% save wave1 eventStereotypeStored
