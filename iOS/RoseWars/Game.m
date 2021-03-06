//
//  Game.m
//  WarOfTheRoses
//
//  Created by Heine Skov Kristensen on 1/5/13.
//
//

#import "Game.h"
#import "CardForSerialization.h"
#import "GCTurnBasedMatchHelper.h"
#import "CardPool.h"
#import "PathFinderStep.h"
#import "AbilityFactory.h"
#import "MoveAction.h"
#import "GameSerializer.h"

@interface Game()

- (Card*)getCardFromDeck:(Deck*)deck locatedAt:(GridLocation*)locatedAt;

@end

@implementation Game

@synthesize gametype;
@synthesize myDeck = _deck;
@synthesize enemyDeck = _enemyDeck;
@synthesize unitLayout = _unitLayout;

- (id)init {
    
    self = [super init];
    
    if (self) {
        self.myColor = arc4random() % 2;
        
        NSLog(@"My color is initialized to %@", self.myColor == kPlayerGreen ? @"Green" : @"Red");
        
        self.currentRound = 1;
        _unitLayout = [[NSMutableDictionary alloc] init];
        _actionsForPlayback = [[NSMutableArray alloc] init];
        _gameSerializer = [[GameSerializer alloc] init];
        _latestBattleReports = [[NSMutableArray alloc ] init];
    }
    
    return self;
}

- (PlayerColors)enemyColor {
    
    if (self.myColor == kPlayerGreen) {
        return kPlayerRed;
    }
    
    return kPlayerGreen;
}

- (void)populateUnitLayout {
    
    for (Card *card in self.myDeck.cards) {
        if (card.cardLocation != nil) {
            [self.unitLayout setObject:card forKey:card.cardLocation];
        }
    }
    
    for (Card *card in self.enemyDeck.cards) {
        if (card.cardLocation != nil) {
            [self.unitLayout setObject:card forKey:card.cardLocation];
        }
    }
}

- (void)takeCardSnapshot:(CardSnapshotStates)state {
    
    [_gameSerializer takeCardSnapshot:self state:state];
}

- (NSData*)serializeCurrentGameForPlayerWithId:(NSString*)playerId {
    
    [self takeCardSnapshot:kCardSnapshotStateAfterAction];

    return [_gameSerializer serializeGame:self forPlayerWithId:playerId];
}

- (void)deserializeGameData:(NSData *)gameData forPlayerWithId:(NSString*)playerId allPlayers:(NSArray*)allPlayers onlyActions:(BOOL)onlyActions onlyEnemyUnits:(BOOL)onlyEnemyUnits {
    
    [_latestBattleReports removeAllObjects];
    
    [_gameSerializer deserializeGameData:gameData forPlayerWithId:playerId allPlayers:allPlayers toGame:self onlyActions:onlyActions onlyEnemyUnits:onlyEnemyUnits];
}

- (void)addBattleReport:(BattleReport*)battlereport forAction:(Action*)action {
    
    if (!action.playback) {
        [_latestBattleReports addObject:battlereport];
    }
}

- (Card *)getCardFromDeck:(Deck *)deck locatedAt:(GridLocation *)locatedAt {
    
    for (Card *card in deck.cards) {
        
        if ([card.cardLocation isSameLocationAs:locatedAt]) {
            return card;
        }
    }
    
    return nil;
}

@end
